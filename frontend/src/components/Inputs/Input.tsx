import { type ChangeEvent } from "react";

interface InputProps {
  placeholder: string;
  type?: string;
  value: string;
  onChange: (e: ChangeEvent<HTMLInputElement>) => void;
  required?: boolean;
  pattern?: string;
  inputMode?: "text" | "numeric" | "decimal" | "tel";
}

const Input = ({
  placeholder,
  type = "text",
  value,
  onChange,
  required,
  pattern,
  inputMode,
}: InputProps) => (
  <div className="w-full max-w-[450px] h-[50px]">
    <input
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      required={required}
      pattern={pattern}
      inputMode={inputMode}
      className="w-full h-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
  </div>
);

export default Input;
