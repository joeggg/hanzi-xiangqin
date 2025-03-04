export default async function TestPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  console.log(id);
  return (
    <div>
      <h1>Test ID: {id}</h1>
    </div>
  );
}
