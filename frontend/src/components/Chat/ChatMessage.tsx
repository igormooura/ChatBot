import { Bot, User } from "lucide-react";

interface Message {
  sender: "user" | "bot";
  text: string;
  timestamp: string; 
}

interface ChatMessageProps {
  messages: Message;
}

const ChatMessage = ({ messages }: ChatMessageProps) => {
  const isUser = messages.sender === "user";
  const isBot = messages.sender === 'bot';

  const formatTime = (isoString: string) => {
    const date = new Date(isoString);
    const hours = date.getHours().toString().padStart(2, "0");
    const minutes = date.getMinutes().toString().padStart(2, "0");
    return `${hours}:${minutes}`;
  };

  return (
    <div className={`flex mb-4 ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`flex flex-col max-w-[80%] md:max-w-[70%] px-5 py-3.5 rounded-2xl
          ${isUser
            ? "bg-white text-black shadow-md"
            : "bg-gray-200 text-black rounded-bl-none"
          }`}
      >
  
        {isBot && (
          <div className="mb-1 text-sm font-semibold text-gray-700">
            Assistente virtual
          </div>
        )}

        {isUser && (
          <div className="mb-1 text-sm font-semibold text-gray-700">
            Você
          </div>
        )}

        <div className="flex items-start">
          <div className={`flex-shrink-0 mr-3 ${isUser ? "text-indigo-200" : "text-gray-600"}`}>
            {isUser ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
          </div>
          <div>{messages.text}</div>
        </div>

        <div className={`mt-1 text-xs ${isUser ? "text-black/80 text-right" : "text-gray-600"}`}>
          {formatTime(messages.timestamp)}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
