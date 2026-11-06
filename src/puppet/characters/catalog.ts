import type { PuppetDefinition } from '../PuppetDefinition';
import { wayang01 } from './wayang01';
import { wayang02 } from './wayang02';
import { wayang03 } from './wayang03';
import { wayang04 } from './wayang04';

export interface CharacterEntry {
  id: string;
  name: string;
  definition: PuppetDefinition;
  thumbnail?: string;
  available: boolean;
}
export const characterCatalog: readonly CharacterEntry[] = [wayang01, wayang02, wayang03, wayang04]
  .map(definition => ({ id: definition.id, name: definition.name, definition,
    thumbnail: definition.assets.reference ?? definition.assets.body, available: true }));
