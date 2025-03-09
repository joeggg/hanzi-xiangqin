import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import Image from "next/image";
import Link from "next/link";
import localFont from "next/font/local";

const yrdzst = localFont({ src: "./fonts/yrdzst_regular.ttf" });

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Hanzi Xiangqin",
  description: "Test your knowledge of Chinese characters",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <Theme>
          <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
            <header
              className={`row-start-1 flex gap-16 items-center ${yrdzst.className} text-4xl font-bold`}
            >
              <h1 className="">
                <Link href="/">hanzi</Link>
                <br />
                <Link href="/">xiangqin</Link>
              </h1>
              <h1 className="text-justify">
                <Link href="/">汉字</Link>
                <br />
                <Link href="/">相亲</Link>
              </h1>
            </header>
            <main className="flex flex-col gap-8 row-start-2 absolute w-full items-center">
              {children}
            </main>
          </div>
          <footer className="row-start-3 flex gap-6 flex-wrap items-center justify-center">
            <a
              className="flex items-center gap-2 hover:underline hover:underline-offset-4"
              href="https://github.com/joeggg/hanzi-xiangqin"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Image
                aria-hidden
                src="/file.svg"
                alt="File icon"
                width={16}
                height={16}
              />
              View Source
            </a>
          </footer>
        </Theme>
      </body>
    </html>
  );
}
