import { Send } from "lucide-react";

interface ChatInputsProps {
  input: string;
  setInput: (value: string) => void;
  loading: boolean;
  onSend: () => void;
}

const ChatInputs = ({ input, setInput, loading, onSend }: ChatInputsProps) => {
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !loading && input.trim()) {
      onSend();
    }
  };

  return (
    <div className="w-full mx-auto mt-4 px-4">
  <div className="flex items-center space-x-3">
    <input
      type="text"
      value={input}
      onChange={(e) => setInput(e.target.value)}
      onKeyDown={handleKeyPress}
      disabled={loading}
      placeholder="Escreva sua mensagem"
      className="flex-1 border bg-white/70 border-gray-300 text-black rounded-full px-5 py-3 
      focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:opacity-50"
    />

    <button
      onClick={onSend}
      disabled={loading || !input.trim()}
      className="p-3 rounded-full transition-colors bg-blue-500 hover:bg-blue-600 text-white shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <Send className="w-5 h-5" />
    </button>
  </div>
</div>

  );
};

export default ChatInputs;
