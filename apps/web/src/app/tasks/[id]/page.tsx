import { EntityDetail } from "@/components/phase2-crud";

export default async function TaskDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <EntityDetail entityType="tasks" id={id} />;
}
