import { useState } from 'react';

interface ManualExamSlotsProps {
  date: string;
  horarios: Record<string, string[]>;
  onFinalize: (selecoes: Record<string, string>) => void;
}

const ManualExamSlots = ({ date, horarios, onFinalize }: ManualExamSlotsProps) => {
  const [selectedSlots, setSelectedSlots] = useState<Record<string, string>>({});

  const handleSelectSlot = (examName: string, slot: string) => {
    setSelectedSlots(prev => ({ ...prev, [examName]: slot }));
  };

  const formattedDate = new Date(date + "T12:00:00").toLocaleDateString('pt-BR', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  });

  return (
    <div className="flex justify-start mb-2">
      <div className="ml-12 p-4 bg-gray-50 rounded-lg space-y-4 shadow-md max-w-md w-full">
        <div className="text-center border-b pb-2 mb-2">
            <h3 className="font-bold text-gray-800">Horários Disponíveis</h3>
            <p className="text-sm font-semibold text-blue-600">{formattedDate}</p>
        </div>
        {Object.entries(horarios).map(([examName, slots]) => (
          <div key={examName}>
            <h4 className="font-bold text-lg text-gray-800 mb-2">{examName}</h4>
            <div className="flex flex-wrap gap-2">
              {slots.map((slot) => (
                <button
                  key={slot}
                  onClick={() => handleSelectSlot(examName, slot)}
                  className={`font-semibold py-1 px-3 rounded-lg text-sm transition-colors duration-200 ${selectedSlots[examName] === slot ? 'bg-blue-500 text-white shadow-md' : 'bg-green-200 hover:bg-green-400 text-green-800'}`}>
                  {new Date(slot).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </button>
              ))}
            </div>
          </div>
        ))}
        <div className="flex justify-center pt-4 border-t border-gray-200">
            <button 
                onClick={() => onFinalize(selectedSlots)}
                className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-full disabled:bg-gray-400"
                disabled={Object.keys(selectedSlots).length !== Object.keys(horarios).length}
            >
                Agendar Horários Selecionados
            </button>
        </div>
      </div>
    </div>
  );
};

export default ManualExamSlots;