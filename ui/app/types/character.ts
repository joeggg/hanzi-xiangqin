export interface Character {
  simplified: string;
  traditional: string;
  rank: number;
  definitions: Definition[];
}

export interface Definition {
  pinyin: string;
  text: string;
}
