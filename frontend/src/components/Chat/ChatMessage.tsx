import { Bot, User } from "lucide-react";

interface Message {
  sender: "user" | "bot";
  text?: string;
  timestamp: string;
}

interface ChatMessageProps {
  messages: Message;
}

const ChatMessage = ({ messages }: ChatMessageProps) => {
  if (!messages.text) {
    return null;
  }

  const isUser = messages.sender === "user";
  const isBot = messages.sender === "bot";

  const formatTime = (isoString: string) => {
    const date = new Date(isoString);
    const hours = date.getHours().toString().padStart(2, "0");
    const minutes = date.getMinutes().toString().padStart(2, "0");
    return `${hours}:${minutes}`;
  };

  const renderFormattedText = (textWithMarkers: string) => {
    const parts = textWithMarkers.split('###');

    return parts.map((part, index) => {
      if (index % 2 === 1) {
        return <h4 key={index} className="font-bold text-blue-900 mt-4 mb-2 text-lg">{part.trim()}</h4>;
      }

      return part.split('\n').map((line, lineIndex) => {
        if (line.trim() === '') return null;
        return <p key={`${index}-${lineIndex}`} className="text-black leading-relaxed">{line.trim()}</p>;
      });
    });
  };

  return (
    <div className={`flex mb-4 ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`flex flex-col max-w-[80%] md:max-w-[70%] px-5 py-3.5 rounded-2xl
          ${
            isUser
              ? "bg-white text-black shadow-md"
              : "bg-gray-200 text-black rounded-bl-none"
          }`}
      >
        <div className="flex items-center mb-2">
            {isBot && <Bot className="h-5 w-5 mr-3 flex-shrink-0 text-gray-600" />}
            <div className="text-sm font-semibold text-gray-700">
              {isBot ? "Assistente virtual" : "Você"}
            </div>
        </div>
        
        <div className="prose prose-blue max-w-none">
          {isBot ? renderFormattedText(messages.text) : <p>{messages.text}</p>}
        </div>

        <div
          className={`mt-2 text-xs ${
            isUser ? "text-black/80 text-right" : "text-gray-600 text-left"
          }`}
        >
          {formatTime(messages.timestamp)}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;