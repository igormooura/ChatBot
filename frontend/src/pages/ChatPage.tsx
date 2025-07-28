import { useEffect, useRef, type ChangeEvent } from "react";
import Background from "../components/Background/Background";
import Header from "../components/Header/Header";
import ChatContainer from "../components/Chat/ChatContainer";
import LoadingIndicator from "../components/Chat/LoadingIndicator";
import ChatInputs from "../components/Chat/ChatInputs";
import ChatMessage from "../components/Chat/ChatMessage";
import HorarioSlots from "../components/Chat/HorarioSlots";
import OptionButtons from "../components/Chat/OptionButtons";
import ExamSelector from "../components/Chat/ExamSelector";
import SugestaoExame from "../components/Chat/SugestaoExame";
import ManualExamSlots from "../components/Chat/ManualExamSlots";
import DiasSugeridos from "../components/Chat/DiasSugeridos";
import { useChat } from "../hooks/useChat";

const FileUploadButton = ({ onFileUpload }: { onFileUpload: (file: File) => void }) => {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) onFileUpload(e.target.files[0]);
    };
    const handleClick = () => fileInputRef.current?.click();

    return (
        <div className="flex justify-start mb-4 ml-12">
            <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept=".pdf"/>
            <button onClick={handleClick} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full">
                Anexar Guia de Exame (PDF)
            </button>
        </div>
    );
};

const ChatPage = () => {
  const {
    messages, isLoading, input, setInput, chatState, selectedSlots,
    handleSendMessage, handleSelectSlot, handleFinalize, handleStartAgendamento, 
    handleStartSugestao, handleFinalizeManualSelection, 
    // ✅ CORRIGIDO: Importar a nova função do hook
    handleDaySuggestionConfirmation
  } = useChat();

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const showInput = ["AWAITING_REQUEST", "AWAITING_CONFIRMATION_DETAILS", "AWAITING_SUGGESTION_INPUT", "AWAITING_EXAM_SELECTION_AND_DATE", "AWAITING_EXAM_CONFIRMATION_DETAILS", "AWAITING_MANUAL_EXAM_CONFIRMATION_DETAILS"].includes(chatState);

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
                  {msg.upload && <FileUploadButton onFileUpload={msg.upload.onFileUpload} />}
                  {msg.examSelector && <ExamSelector exams={msg.examSelector.exams} onSelectionChange={msg.examSelector.onSelectionChange} />}
                  {msg.sugestaoExames && <SugestaoExame sugestao={msg.sugestaoExames} />}
                  
                  {/* ✅ CORRIGIDO: Lógica de renderização para DiasSugeridos */}
                  {msg.diasSugeridos && (
                    <DiasSugeridos
                      sugestoes={msg.diasSugeridos.sugestoes}
                      isConfirmed={msg.diasSugeridos.isConfirmed}
                      onConfirm={handleDaySuggestionConfirmation}
                    />
                  )}

                  {msg.horariosExames && <ManualExamSlots date={msg.horariosExames.date} horarios={msg.horariosExames.slots} onFinalize={handleFinalizeManualSelection} />}
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