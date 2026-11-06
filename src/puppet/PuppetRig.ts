import { Assets, Container, Sprite, Texture } from 'pixi.js';
import type { PuppetDefinition, PuppetPoint } from './PuppetDefinition';

type PuppetTextures = Record<string, Texture>;

export class PuppetRig {
  readonly root = new Container({ label: 'WayangRoot', eventMode: 'none' });
  private readonly joints = new Map<string, { shoulder: Container; elbow: Container }>();
  private facingScale = 1;

  static assetPaths(definition: PuppetDefinition): string[] {
    // Reference is for selection/development only, never a gameplay dependency.
    return [...new Set([definition.assets.body,
      ...(definition.assets.mainRod ? [definition.assets.mainRod] : []),
      ...definition.arms.flatMap(arm => [arm.upperArmAsset, arm.forearmHandAsset])])];
  }

  static assetCount(definition: PuppetDefinition): number { return this.assetPaths(definition).length; }

  static async load(definition: PuppetDefinition, onAsset?: () => void): Promise<PuppetRig> {
    const textures: PuppetTextures = {};
    const results = await Promise.allSettled(this.assetPaths(definition).map(async path => {
      textures[path] = await Assets.load<Texture>(path);
      onAsset?.();
    }));
    const failure = results.find(result => result.status === 'rejected');
    if (failure?.status === 'rejected') throw failure.reason;
    return new PuppetRig(definition, textures);
  }

  static async unload(definition: PuppetDefinition): Promise<void> {
    await Promise.all(this.assetPaths(definition).map(path => Assets.cache.has(path) ? Assets.unload(path) : undefined));
  }

  constructor(readonly definition: PuppetDefinition, textures: PuppetTextures) {
    this.root.pivot.set(definition.rootPivot.x, definition.rootPivot.y);
    const layers = new Map<string, Container>();
    layers.set('body', this.createSprite('Body', textures[definition.assets.body]));
    if (definition.assets.mainRod) {
      layers.set('mainRod', this.createSprite('MainRod', textures[definition.assets.mainRod]));
    }
    for (const arm of definition.arms) {
      const joints = this.createArm(arm.id, arm.shoulderPivot, arm.elbowPivot,
        textures[arm.upperArmAsset], textures[arm.forearmHandAsset]);
      this.joints.set(arm.id, joints);
      layers.set(arm.id, joints.shoulder);
    }
    for (const layer of definition.layers) {
      const child = layers.get(layer);
      if (child) this.root.addChild(child);
    }
    this.resetPose();
  }

  setPosition(x: number, y: number): void { this.root.position.set(x, y); }
  get horizontalDirection(): number { return this.facingScale; }

  setFacing(facing: 'left' | 'right'): void {
    this.facingScale = facing === this.definition.artworkFacing ? 1 : -1;
    this.setScale(Math.abs(this.root.scale.y));
  }

  setScale(scale: number): void { this.root.scale.set(scale * this.facingScale, scale); }
  flipFacing(): void {
    this.facingScale *= -1;
    this.setScale(Math.abs(this.root.scale.y));
  }
  setBodyRotation(rotation: number): void {
    if (Number.isFinite(rotation)) this.root.rotation = rotation;
  }

  setArmRotation(id: string, shoulder: number, elbow: number): void {
    const joints = this.joints.get(id);
    const arm = this.definition.arms.find(candidate => candidate.id === id);
    if (!joints || !arm) return;
    if (Number.isFinite(shoulder)) joints.shoulder.rotation = Math.min(arm.shoulderMaxRotation, Math.max(arm.shoulderMinRotation, shoulder));
    if (Number.isFinite(elbow)) joints.elbow.rotation = Math.min(arm.elbowMaxRotation, Math.max(arm.elbowMinRotation, elbow));
  }

  resetPose(): void {
    this.setBodyRotation(0);
    for (const arm of this.definition.arms) this.setArmRotation(arm.id, 0, 0);
  }

  destroy(): void {
    // Session unloads cached textures only after all active rigs are destroyed.
    this.root.destroy({ children: true });
  }

  private createSprite(label: string, texture: Texture): Sprite {
    const sprite = new Sprite({ label, texture });
    const { width, height } = this.definition.canvas;
    // Uniformly map the complete PNG into the logical canvas. No cropping,
    // anchor changes or independent X/Y scaling; full-canvas alignment survives.
    sprite.scale.set(Math.min(width / texture.width, height / texture.height));
    return sprite;
  }

  private createArm(
    side: string,
    shoulderPivot: PuppetPoint,
    elbowPivot: PuppetPoint,
    upperTexture: Texture,
    forearmTexture: Texture,
  ): { shoulder: Container; elbow: Container } {
    const shoulder = new Container({ label: `${side}Shoulder` });
    shoulder.position.set(shoulderPivot.x, shoulderPivot.y);

    // Keep the elbow under an unscaled upper-arm container, never under the
    // full-canvas sprite whose scale converts native pixels to logical units.
    const upperArm = new Container({ label: `${side}UpperArm` });
    const upperSprite = this.createSprite(`${side}UpperArmArtwork`, upperTexture);
    upperSprite.position.set(-shoulderPivot.x, -shoulderPivot.y);
    shoulder.addChild(upperArm);
    upperArm.addChild(upperSprite);

    const elbow = new Container({ label: `${side}Elbow` });
    elbow.position.set(
      elbowPivot.x - shoulderPivot.x,
      elbowPivot.y - shoulderPivot.y,
    );
    const forearm = this.createSprite(`${side}ForearmHand`, forearmTexture);
    forearm.position.set(-elbowPivot.x, -elbowPivot.y);
    upperArm.addChild(elbow);
    elbow.addChild(forearm);
    return { shoulder, elbow };
  }
}
