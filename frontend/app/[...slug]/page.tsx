import Dashboard from "@/components/Dashboard";
import WorkspacePage from "@/components/WorkspacePage";

export default async function WorkspaceRoute({ params }: { params: Promise<{ slug: string[] }> }) {
  const { slug } = await params;
  if (slug.length === 1 && slug[0] === "dashboard") return <Dashboard />;
  return <WorkspacePage kind={slug[0] ?? "dashboard"} detail={slug.slice(1)} />;
}
