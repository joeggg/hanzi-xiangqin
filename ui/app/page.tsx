"use client";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { Button } from "@radix-ui/themes";

export default function Home() {
  const baseUrl = "http://192.168.0.15:8000";
  const router = useRouter();

  const startTest = async () => {
    try {
      const response = await fetch(`${baseUrl}/tests/start`);
      const data = await response.json();
      if (data.test_id) {
        router.push(`/test/${data.test_id}`);
      }
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <header className="row-start-1 flex gap-16 items-center">
        <h1 className="text-3xl font-bold">
          hanzi
          <br />
          xiangqin
        </h1>
        <h1 className="text-3xl font-bold text-justify">
          汉字
          <br />
          相亲
        </h1>
      </header>
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start">
        <Button size="4" variant="surface" color="jade" onClick={startTest}>
          Start Test!
        </Button>
      </main>
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
    </div>
  );
}
