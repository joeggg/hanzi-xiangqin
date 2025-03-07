"use client";

import { useRouter } from "next/navigation";
import { Button } from "@radix-ui/themes";

import client from "app/tools/client";

export default function Home() {
  const router = useRouter();

  const startTest = async () => {
    try {
      const response = await client.get(`/tests/start`);
      const data = await response.data;
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
