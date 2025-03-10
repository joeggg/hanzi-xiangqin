import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { cookies } from "next/headers";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";

import Header from "./components/header";
import Footer from "./components/footer";
import "./globals.css";

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

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookiesStore = await cookies();
  const theme = cookiesStore.get("theme") || { value: "light" };

  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased h-full`}
      >
        {/* @ts-expect-error theme is light or dark */}
        <Theme appearance={theme.value}>
          <div
            className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center p-8 pb-20
            gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]"
            style={{ minHeight: "90vh" }}
          >
            <Header />
            <main className="flex flex-col gap-8 row-start-2 absolute w-full items-center">
              {children}
            </main>
          </div>
          <Footer />
        </Theme>
      </body>
    </html>
  );
}
