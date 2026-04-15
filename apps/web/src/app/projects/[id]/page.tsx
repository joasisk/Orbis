import { EntityDetail } from "@/components/phase2-crud";

export default async function ProjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <EntityDetail entityType="projects" id={id} />;
}
