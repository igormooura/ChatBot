import type  { OptionButtonProps } from "../../types/chat";

interface OptionButtonsProps {
  options: OptionButtonProps[];
}

const OptionButtons = ({ options }: OptionButtonsProps) => (
  <div className="flex flex-wrap justify-start gap-2 mb-4 ml-12">
    {options.map((opt, i) => (
      <button key={i} onClick={opt.onClick} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full">
        {opt.text}
      </button>
    ))}
  </div>
);

export default OptionButtons;