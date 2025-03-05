"use client";

import { useRouter } from "next/navigation";
import { Button } from "@radix-ui/themes";

export default function Home() {
  const router = useRouter();

  const startTest = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BASE_URL}/tests/start`,
      );
      const data = await response.json();
      if (data.test_id) {
        router.push(`/test/${data.test_id}`);
      }
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div>
      <Button size="4" variant="surface" color="jade" onClick={startTest}>
        Start Test!
      </Button>
    </div>
  );
}
