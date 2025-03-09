export const isMobile = (): boolean => {
  return window.matchMedia("(max-width: 640px)").matches;
};
