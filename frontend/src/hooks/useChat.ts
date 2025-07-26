import { useState, useEffect, useRef } from "react";
import axios from "axios";
import type { Message, ChatState, HorarioResponse } from "../types/chat";

const API_BASE_URL = "http://localhost:5000/api/agendamento";
const API_BUSCAR_HORARIOS = `${API_BASE_URL}/buscar-horarios`;
const API_CONFIRMAR_AGENDAMENTO = `${API_BASE_URL}/confirmar-agendamento`;
const API_SUGERIR_ESPECIALISTA = `${API_BASE_URL}/sugerir-especialista`;

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [input, setInput] = useState("");
  const [chatState, setChatState] = useState<ChatState>("INITIAL");
  const [selectedSlots, setSelectedSlots] = useState<Record<string, HorarioResponse>>({});
  const initialEffectRan = useRef(false);

  const addBotMessage = (message: Omit<Message, "id" | "sender" | "timestamp">) => {
    setMessages((prev) => [...prev, { id: Date.now(), sender: "bot", timestamp: new Date().toISOString(), ...message }]);
  };

  const handleStartAgendamento = () => {
    addBotMessage({ text: "Ótimo! Por favor, me diga qual especialista(s) e para qual dia e período você gostaria de agendar. (Ex: cardiologista e dermatologista para amanhã à tarde)" });
    setChatState("AWAITING_REQUEST");
    setSelectedSlots({});
  };

  const handleStartSugestao = () => {
    addBotMessage({ text: "Claro! Por favor, descreva seus sintomas para que eu possa sugerir um especialista." });
    setChatState("AWAITING_SUGGESTION_INPUT");
  };

  useEffect(() => {
    if (chatState === "INITIAL" && !initialEffectRan.current) {
      addBotMessage({
        text: "Olá! Sou seu assistente de agendamento. O que você gostaria de fazer?",
        options: [
          { text: "Agendar Consulta", onClick: handleStartAgendamento },
          { text: "Sugerir Especialista", onClick: handleStartSugestao },
          { text: "Marcar Exame", onClick: () => addBotMessage({ text: "Esta função será implementada em breve!" }) },
        ],
      });
      initialEffectRan.current = true;
    }
  }, [chatState]);

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;
    const userMessageText = input;
    setMessages((prev) => [...prev, { id: Date.now(), sender: "user", text: userMessageText, timestamp: new Date().toISOString() }]);
    setInput("");
    setIsLoading(true);

    try {
      if (chatState === "AWAITING_REQUEST") {
        const response = await axios.post(API_BUSCAR_HORARIOS, { pedido: userMessageText });
        if (response.data.horarios_encontrados.length > 0) {
          addBotMessage({ text: "Encontrei os seguintes horários. Selecione um por especialista, se desejar:" });
          addBotMessage({ horarios: response.data.horarios_encontrados });
        } else {
          addBotMessage({ text: "Desculpe, não encontrei horários. Você pode tentar outra data/período?" });
        }
      } else if (chatState === "AWAITING_SUGGESTION_INPUT") {
        const response = await axios.post(API_SUGERIR_ESPECIALISTA, { sintomas: userMessageText });
        const { explicacao, sugestoes } = response.data;
        
        addBotMessage({ text: explicacao });

        if (sugestoes && sugestoes.length > 0) {
          addBotMessage({
            text: `Com base nos seus sintomas, os especialistas mais indicados são: ${sugestoes.join(', ')}. O que você gostaria de fazer?`,
            options: [
              { text: "Agendar uma consulta", onClick: handleStartAgendamento },
              { text: "Verificar outros sintomas", onClick: handleStartSugestao }
            ]
          });
        }
        setChatState("INITIAL"); 

      } else if (chatState === "AWAITING_CONFIRMATION_DETAILS") {
        const [email, cpf] = userMessageText.split(",").map((s) => s.trim());
        if (!email || !cpf) {
          addBotMessage({ text: "Formato inválido. Por favor, informe seu email e CPF, separados por vírgula." });
          return;
        }
        const agendamentosParaEnviar = Object.values(selectedSlots).map(slot => ({ medico_id: slot.medico_id, horario: slot.horario }));
        const response = await axios.post(API_CONFIRMAR_AGENDAMENTO, { email, cpf, agendamentos: agendamentosParaEnviar });
        addBotMessage({ text: response.data.mensagem });
        addBotMessage({ options: [{ text: "Ver Minhas Consultas", onClick: () => addBotMessage({ text: "Esta página será criada no futuro!" }) }] });
        setChatState("CONFIRMED");
        setSelectedSlots({});
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.explicacao || error.response?.data?.mensagem || "Ocorreu um erro. Tente novamente.";
      addBotMessage({ text: errorMessage });
      addBotMessage({
        options: [
          { text: "Tentar agendar novamente", onClick: handleStartAgendamento },
          { text: "Tentar sugerir novamente", onClick: handleStartSugestao }
        ]
      });
      setChatState("INITIAL");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectSlot = (slot: HorarioResponse) => {
    setSelectedSlots(prev => ({ ...prev, [slot.especialista]: slot }));
  };

  const handleFinalize = () => {
    if (Object.keys(selectedSlots).length === 0) {
      addBotMessage({ text: "Nenhuma consulta foi selecionada para agendar." });
      return;
    }
    const selections = Object.values(selectedSlots).map(s => `${s.especialista} às ${new Date(s.horario).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`).join(', ');
    addBotMessage({ text: `Ok, vamos confirmar: ${selections}. Para finalizar, por favor, informe seu email e CPF, separados por vírgula.` });
    setChatState("AWAITING_CONFIRMATION_DETAILS");
  };

  return {
    messages,
    isLoading,
    input,
    setInput,
    chatState,
    selectedSlots,
    handleSendMessage,
    handleSelectSlot,
    handleFinalize,
    handleStartAgendamento,
    handleStartSugestao
  };
};