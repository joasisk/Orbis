import { EntityDetailView } from "@/components/entity-management";

export default async function ProjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <EntityDetailView entityType="projects" id={id} />;
}
