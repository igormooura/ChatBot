import { useState } from 'react';
import type { SugestaoExame } from "../../types/chat";
interface DiasSugeridosProps {
  sugestoes: SugestaoExame[][];
  isConfirmed: boolean;
  onConfirm: (sugestao: SugestaoExame[]) => void;
}

const DiasSugeridos = ({ sugestoes, isConfirmed, onConfirm }: DiasSugeridosProps) => {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  if (!sugestoes || sugestoes.length === 0) return null;

  const handleConfirmClick = () => {
    if (selectedIndex !== null) {
      onConfirm(sugestoes[selectedIndex]);
    }
  };

  const handleSelect = (index: number) => {
    if (!isConfirmed) {
      setSelectedIndex(index);
    }
  }

  return (
    <div className="flex justify-start mb-2">
      <div className="ml-12 p-4 bg-gray-50 rounded-lg space-y-4 shadow-md max-w-lg w-full">
        <div className="space-y-3">
      
          {sugestoes.map((sugestao: SugestaoExame[], index) => {
            const date = new Date(sugestao[0].horario);
            const formattedDate = date.toLocaleDateString('pt-BR', { weekday: 'long', day: '2-digit', month: 'short' });
            const isSelected = selectedIndex === index;

            return (
              <div
                key={index}
                onClick={() => handleSelect(index)}
                className={`
                  p-3 rounded-lg border-2 transition-all
                  ${isConfirmed && !isSelected ? 'bg-gray-200 opacity-60' : ''}
                  ${isSelected ? 'bg-blue-100 border-blue-500 shadow-lg' : 'bg-white border-gray-200'}
                  ${!isConfirmed ? 'cursor-pointer hover:bg-gray-100' : 'cursor-default'}
                `}
              >
                <p className="font-bold text-lg text-blue-800 mb-2">{formattedDate}</p>
                <div className="space-y-1 pl-2 border-l-2 border-gray-300">
                  {sugestao.map((item, itemIndex) => (
                    <div key={itemIndex} className="flex justify-between items-center text-sm">
                      <span className="font-semibold text-gray-700">{item.exame}</span>
                      <span className="ml-4 text-white bg-green-600 font-bold px-3 py-1 rounded-full text-xs">
                        {new Date(item.horario).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>

        {!isConfirmed && (
          <div className="pt-4 border-t border-gray-200 flex justify-center">
            <button
              onClick={handleConfirmClick}
              disabled={selectedIndex === null}
              className="w-full sm:w-auto bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-6 rounded-full transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              Confirmar Dia Selecionado
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default DiasSugeridos;