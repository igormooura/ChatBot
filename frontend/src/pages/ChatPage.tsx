import Background from "../components/Background/Background";
import ChatMessage from "../components/Chat/ChatMessage";
import Header from "../components/Header/Header";
import ChatContainer from "../components/Chat/ChatContainer";
import LoadingIndicator from "../components/Chat/LoadingIndicator";
import ChatInputs from "../components/Chat/ChatInputs";
import { useState } from "react";

type Message = {
  id: number;
  sender: "user" | "bot";
  text: string;
  timestamp: string;
};

const ChatPage = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [input, setInput] = useState("");

  const handleSendMessage = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now(),
      sender: "user",
      text: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    setTimeout(() => {
      // pra simular o bot
      const botMessage: Message = {
        id: Date.now() + 1,
        sender: "bot",
        text: "Entendi! Em que mais posso ajudar?",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, botMessage]);
      setIsLoading(false);
    }, 2000);
  };

  return (
    <Background>
      <Header />
      <div className="flex justify-center">
        <ChatContainer>
          {/* definitivamente nao sei se é uma boa pratica colocar esse 70vh */}
          <div className="flex flex-col h-[70vh] max-w-5xl mx-auto"> 
            <div className="flex-grow overflow-y-auto px-4 py-2">
              {messages.map((msg) => (
                <ChatMessage key={msg.id} messages={msg} />
              ))}
              {isLoading && (
                <div className="flex mb-4 justify-start">
                  <LoadingIndicator />
                </div>
              )}
            </div>
            <ChatInputs
              input={input}
              setInput={setInput}
              loading={isLoading}
              onSend={handleSendMessage}
            />
          </div>
        </ChatContainer>
      </div>
    </Background>
  );
};

export default ChatPage;
