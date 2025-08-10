import MachineDetails from "@/components/MachineDetails";

interface MachinePageProps {
  params: {
    id: string;
  };
}

export default function MachinePage({ params }: MachinePageProps) {
  const machineId = parseInt(params.id);
  
  if (isNaN(machineId)) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-sm p-8 text-center max-w-md">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            ID de machine invalide
          </h2>
          <p className="text-gray-600 mb-4">
            L'identifiant de la machine n'est pas valide
          </p>
        </div>
      </div>
    );
  }

  return <MachineDetails machineId={machineId} />;
} 