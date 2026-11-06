/** Accumulate observed presence without treating slow inference as a missing hand. */
export class HandCalibration {
  private previousTimestamp?: number;
  private heldMilliseconds = 0;

  update(allPresent: boolean, timestamp: number): boolean {
    if (!allPresent) {
      this.reset();
      return false;
    }
    if (this.previousTimestamp !== undefined) {
      this.heldMilliseconds += Math.min(300, Math.max(0, timestamp - this.previousTimestamp));
    }
    this.previousTimestamp = timestamp;
    return this.heldMilliseconds >= 1500;
  }

  reset(): void {
    this.previousTimestamp = undefined;
    this.heldMilliseconds = 0;
  }
}
