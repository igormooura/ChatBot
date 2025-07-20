import type { HorarioResponse } from "../../types/chat";

interface HorarioSlotsProps {
  horarios: HorarioResponse[];
  selectedSlots: Record<string, HorarioResponse>;
  onSelectSlot: (slot: HorarioResponse) => void;
  onFinalize: () => void;
  onNewSearch: () => void;
}

const HorarioSlots = ({ horarios, selectedSlots, onSelectSlot, onFinalize, onNewSearch }: HorarioSlotsProps) => {
  const groupedBySpecialist = horarios.reduce((acc, slot) => {
    const specialist = slot.especialista;
    if (!acc[specialist]) acc[specialist] = [];
    acc[specialist].push(slot);
    return acc;
  }, {} as Record<string, HorarioResponse[]>);

  const dateOfSlots = horarios.length > 0 ? new Date(horarios[0].horario) : null;
  const formattedDate = dateOfSlots ? dateOfSlots.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' }) : '';

  return (
    <div className="relative mb-4 ml-12 p-4 bg-gray-50 rounded-lg space-y-4">
      {formattedDate && (
        <div className="absolute top-4 right-4 text-sm font-semibold text-gray-500 bg-gray-200 px-2 py-1 rounded">
          {formattedDate}
        </div>
      )}
      {Object.entries(groupedBySpecialist).map(([specialist, slots]) => (
        <div key={specialist}>
          <h4 className="font-bold text-lg text-gray-800 mb-2">{specialist}</h4>
          {slots.map((slot) => (
            <button
              key={slot.horario}
              onClick={() => onSelectSlot(slot)}
              className={`mr-2 mb-2 font-semibold py-1 px-3 rounded-lg text-sm transition-colors duration-200 ${selectedSlots[specialist]?.horario === slot.horario ? 'bg-blue-500 text-white shadow-md' : 'bg-green-200 hover:bg-green-400 text-green-800'}`}>
              {slot.medico_nome}: {new Date(slot.horario).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </button>
          ))}
        </div>
      ))}
      <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-gray-200">
        <button onClick={onFinalize} className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-full">
          Finalizar Agendamento
        </button>
        <button onClick={onNewSearch} className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-full">
          Fazer Nova Busca
        </button>
      </div>
    </div>
  );
};

export default HorarioSlots;