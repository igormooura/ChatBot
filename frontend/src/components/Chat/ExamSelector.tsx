import { useState } from 'react';

interface ExamSelectorProps {
  exams: string[];
  onSelectionChange: (selectedExams: string[]) => void;
}

const ExamSelector = ({ exams, onSelectionChange }: ExamSelectorProps) => {
  const [selected, setSelected] = useState<string[]>([]);

  const handleCheckboxChange = (examName: string) => {
    const newSelection = selected.includes(examName)
      ? selected.filter((name) => name !== examName)
      : [...selected, examName];
    
    setSelected(newSelection);
    onSelectionChange(newSelection);
  };

  return (
    <div className="relative mb-4 ml-12 p-4 bg-gray-50 rounded-lg space-y-3">
      <h4 className="font-bold text-lg text-gray-800 mb-2">Exames Encontrados</h4>
      <div className="flex flex-col">
        {exams.map((exam) => (
          <label key={exam} className="flex items-center space-x-3 p-2 rounded-md hover:bg-blue-100 cursor-pointer">
            <input
              type="checkbox"
              className="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              checked={selected.includes(exam)}
              onChange={() => handleCheckboxChange(exam)}
            />
            <span className="text-gray-700">{exam}</span>
          </label>
        ))}
      </div>
    </div>
  );
};

export default ExamSelector;