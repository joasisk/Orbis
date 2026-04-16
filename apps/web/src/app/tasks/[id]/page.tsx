import { EntityDetailView } from "@/components/entity-management";

export default async function TaskDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <EntityDetailView entityType="tasks" id={id} />;
}
