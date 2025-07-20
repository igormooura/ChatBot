import { useEffect, useRef } from "react";
import Background from "../components/Background/Background";
import Header from "../components/Header/Header";
import ChatContainer from "../components/Chat/ChatContainer";
import LoadingIndicator from "../components/Chat/LoadingIndicator";
import ChatInputs from "../components/Chat/ChatInputs";
import ChatMessage from "../components/Chat/ChatMessage";
import HorarioSlots from "../components/Chat/HorarioSlots";
import OptionButtons from "../components/Chat/OptionButtons";
import { useChat } from "../hooks/useChat";

const ChatPage = () => {
  const {
    messages,
    isLoading,
    input,
    setInput,
    chatState,
    selectedSlots,
    handleSendMessage,
    handleSelectSlot,
    handleFinalize,
    handleStartAgendamento
  } = useChat();

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const showInput = ["AWAITING_REQUEST", "AWAITING_CONFIRMATION_DETAILS"].includes(chatState);

  return (
    <Background>
      <Header />
      <div className="flex justify-center h-[calc(100vh-theme(height.header))]">
        <ChatContainer>
          <div className="flex flex-col h-full max-w-5xl mx-auto">
            <div className="flex-grow overflow-y-auto px-4 py-2 space-y-4">
              {messages.map((msg) => (
                <div key={msg.id}>
                  {msg.text && <ChatMessage messages={msg} />}
                  {msg.options && <OptionButtons options={msg.options} />}
                  {msg.horarios && (
                    <HorarioSlots
                      horarios={msg.horarios}
                      selectedSlots={selectedSlots}
                      onSelectSlot={handleSelectSlot}
                      onFinalize={handleFinalize}
                      onNewSearch={handleStartAgendamento}
                    />
                  )}
                </div>
              ))}
              {isLoading && <div className="flex mb-4 justify-start"><LoadingIndicator /></div>}
              <div ref={chatEndRef} />
            </div>
            {showInput && <ChatInputs input={input} setInput={setInput} loading={isLoading} onSend={handleSendMessage} />}
          </div>
        </ChatContainer>
      </div>
    </Background>
  );
};

export default ChatPage;