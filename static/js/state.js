export const state = {
  run: null,
  get id(){ return this.run?.id || null; }
};
export function setRun(run){ state.run = run; }
