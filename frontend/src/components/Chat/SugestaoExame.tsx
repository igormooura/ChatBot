import type { SugestaoExame as SugestaoExameType } from '../../types/chat';

interface SugestaoExameProps {
  sugestao: SugestaoExameType[];
}

const SugestaoExame = ({ sugestao }: SugestaoExameProps) => {
  if (!sugestao || sugestao.length === 0) return null;

  const dateOfExams = new Date(sugestao[0].horario);
  const formattedDate = dateOfExams.toLocaleDateString('pt-BR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  return (
    <div className="flex justify-start mb-2">
      <div className="ml-12 p-4 bg-white border border-gray-200 rounded-lg space-y-3 shadow-md max-w-md">
        <div className="text-center border-b pb-2 mb-2">
            <h3 className="font-bold text-gray-800">Sugestão de Agendamento:</h3>
            <p className="text-sm font-semibold text-blue-600">{formattedDate}</p>
        </div>
        {sugestao.map((item, index) => (
          <div key={index} className="flex justify-between items-center text-sm">
            <span className="font-semibold text-gray-700">{item.exame}</span>
            <span className="ml-4 text-white bg-green-600 font-bold px-3 py-1 rounded-full">
              {new Date(item.horario).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SugestaoExame;