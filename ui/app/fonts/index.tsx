import { Geist, Geist_Mono } from "next/font/google";
import localFont from "next/font/local";

export const yrdzst = localFont({ src: "./data/YRDZST Regular.ttf" });

export const tegakizatsu = localFont({
  src: "./data/851tegakizatsu Regular.ttf",
});
export const ebas = localFont({ src: "./data/EBAS Medium.ttf" });

export const fontquan = localFont({
  src: "./data/Fontquan-XinYiJiXiangSong Regular.ttf",
});

export const hanyiSentyPagoda = localFont({
  src: "./data/HanyiSentyPagoda Regular.ttf",
});

export const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

export const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});
