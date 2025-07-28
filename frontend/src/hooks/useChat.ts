import { useState, useEffect, useRef } from "react";
import axios from "axios";
import type { Message, ChatState, HorarioResponse, SugestaoExame } from "../types/chat";

const API_AGENDAMENTO_URL = "http://localhost:5000/api/agendamento";
const API_EXAMES_URL = "http://localhost:5000/api/exames";
const API_UPLOAD_URL = "http://localhost:5000/api/upload";

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [input, setInput] = useState("");
  const [chatState, setChatState] = useState<ChatState>("INITIAL");
  const [selectedSlots, setSelectedSlots] = useState<Record<string, HorarioResponse>>({});
  const [selectedExams, setSelectedExams] = useState<string[]>([]);
  const [pendingSuggestion, setPendingSuggestion] = useState<SugestaoExame[] | null>(null);
  const [pendingManualSelections, setPendingManualSelections] = useState<Record<string, string> | null>(null);
  const initialEffectRan = useRef(false);
  const patientId = 1;

  const addBotMessage = (message: Omit<Message, "id" | "sender" | "timestamp">) => {
    setMessages((prev) => [...prev, { id: Date.now(), sender: "bot", timestamp: new Date().toISOString(), ...message }]);
  };

  const handleStartAgendamento = () => {
    addBotMessage({ text: "Ótimo! Por favor, me diga qual especialista(s) e para qual dia e período você gostaria de agendar." });
    setChatState("AWAITING_REQUEST");
    setSelectedSlots({});
  };

  const handleStartSugestao = () => {
    addBotMessage({ text: "Claro! Por favor, descreva seus sintomas para que eu possa sugerir um especialista." });
    setChatState("AWAITING_SUGGESTION_INPUT");
  };

  const handleStartExamFlow = () => {
    addBotMessage({ text: "Entendido. Por favor, anexe o PDF com sua guia de exames.", upload: { onFileUpload: handlePdfUpload } });
    setChatState("AWAITING_EXAM_PDF");
  };

  const handlePdfUpload = async (file: File) => {
    setMessages(prev => prev.filter(m => !m.upload));
    setIsLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const { data } = await axios.post(`${API_UPLOAD_URL}/pdf`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      if (data.exames_encontrados?.length > 0) {
        addBotMessage({ text: "Encontrei estes exames na sua guia. Selecione quais deseja agendar e depois me diga para qual dia e período.", examSelector: { exams: data.exames_encontrados, onSelectionChange: setSelectedExams } });
        setChatState("AWAITING_EXAM_SELECTION_AND_DATE");
      } else {
        addBotMessage({ text: "Não encontrei exames da nossa lista em sua guia." });
        setChatState("INITIAL");
      }
    } catch (error) {
      addBotMessage({ text: "Houve um erro ao processar seu PDF. Tente novamente." });
      setChatState("INITIAL");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (chatState === "INITIAL" && !initialEffectRan.current) {
      addBotMessage({
        text: "Olá! Sou seu assistente de agendamento. O que você gostaria de fazer?",
        options: [
          { text: "Agendar Consulta", onClick: handleStartAgendamento },
          { text: "Sugerir Especialista", onClick: handleStartSugestao },
          { text: "Marcar Exame por PDF", onClick: handleStartExamFlow },
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
        const response = await axios.post(`${API_AGENDAMENTO_URL}/buscar-horarios`, { pedido: userMessageText });
        
        if (response.data.fallback) {
            const { mensagem, pedido_entendido } = response.data;
            addBotMessage({
                text: `${mensagem} O que você gostaria de fazer?`,
                options: [
                    { text: "Ver todos os horários no dia", onClick: () => handleVerTodosHorariosNoDia(pedido_entendido) },
                    { text: "Sugerir próximo dia disponível", onClick: () => handleSugerirProximoDia(pedido_entendido) }
                ]
            });
        } else if (response.data.horarios_encontrados?.length > 0) {
          addBotMessage({ text: "Encontrei os seguintes horários:", horarios: response.data.horarios_encontrados });
        } else {
          addBotMessage({ text: "Desculpe, não foi possível entender seu pedido. Tente ser mais específico sobre o especialista e a data." });
        }
      } else if (chatState === "AWAITING_SUGGESTION_INPUT") {
        const response = await axios.post(`${API_AGENDAMENTO_URL}/sugerir-especialista`, { sintomas: userMessageText });
        const { explicacao, sugestoes } = response.data;
        addBotMessage({ text: explicacao });
        
        if (sugestoes?.length > 0) {
            addBotMessage({
                text: "O que você gostaria de fazer agora?",
                options: [
                    { text: "Agendar Consulta", onClick: handleStartAgendamento },
                    { text: "Digitar sintomas novamente", onClick: handleStartSugestao }
                ]
            });
        }
      } else if (chatState === "AWAITING_CONFIRMATION_DETAILS") {
        const [email, cpf] = userMessageText.split(",").map((s) => s.trim());
        const agendamentos = Object.values(selectedSlots).map(slot => ({ medico_id: slot.medico_id, horario: slot.horario }));
        const response = await axios.post(`${API_AGENDAMENTO_URL}/confirmar-agendamento`, { email, cpf, agendamentos });
        addBotMessage({ text: response.data.mensagem });
        setChatState("CONFIRMED");
      } else if (chatState === "AWAITING_EXAM_SELECTION_AND_DATE") {
        if (selectedExams.length === 0) {
          addBotMessage({ text: "Por favor, selecione pelo menos um exame." });
          setIsLoading(false);
          return;
        }
        await fetchAndDisplaySuggestion(userMessageText);
      } else if (chatState === "AWAITING_EXAM_CONFIRMATION_DETAILS") {
        if (!pendingSuggestion) return;
        const [email, cpf] = userMessageText.split(",").map((s) => s.trim());
        const examNames = pendingSuggestion.map(s => s.exame);
        const startTime = pendingSuggestion[0].horario;
        await axios.post(`${API_EXAMES_URL}/agendar-em-horario-especifico`, { email, cpf, exam_names: examNames, desired_start_time: startTime });
        addBotMessage({ text: "Excelente! Seus exames foram agendados com sucesso." });
        setChatState("CONFIRMED");
      } else if (chatState === "AWAITING_MANUAL_EXAM_CONFIRMATION_DETAILS") {
        if (!pendingManualSelections) return;
        const [email, cpf] = userMessageText.split(",").map((s) => s.trim());
        await axios.post(`${API_EXAMES_URL}/agendar-manual`, { email, cpf, selecoes: pendingManualSelections });
        addBotMessage({ text: "Perfeito! Seus exames selecionados foram agendados com sucesso." });
        setChatState("CONFIRMED");
      }
    } catch (error: any) {
      addBotMessage({ text: error.response?.data?.erro || "Ocorreu um erro." });
      setChatState("INITIAL");
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleVerTodosHorariosNoDia = async (pedido_entendido: any) => {
    setMessages(prev => prev.map(m => ({...m, options: undefined})));
    setIsLoading(true);
    try {
        const pedidoSemPeriodo = { ...pedido_entendido, periodo_dia: 'qualquer' };
        const response = await axios.post(`${API_AGENDAMENTO_URL}/buscar-horarios`, { pedido: `consulta com ${pedidoSemPeriodo.especialistas.join(' e ')} para ${pedidoSemPeriodo.data_base}` });
        
        if (response.data.horarios_encontrados?.length > 0) {
          addBotMessage({ text: `Encontrei todos estes horários para o dia ${new Date(pedido_entendido.data_base).toLocaleDateString('pt-BR', {timeZone: 'UTC'})}:`, horarios: response.data.horarios_encontrados });
        } else {
          addBotMessage({ text: "Realmente não encontrei nenhum horário para os especialistas neste dia. Gostaria de tentar outra data?" });
          setChatState("AWAITING_REQUEST");
        }
    } catch (error) {
        addBotMessage({ text: "Ocorreu um erro ao buscar os horários." });
    } finally {
        setIsLoading(false);
    }
  };

  const handleSugerirProximoDia = async (pedido_entendido: any) => {
    setMessages(prev => prev.map(m => ({...m, options: undefined})));
    setIsLoading(true);
    try {
        const response = await axios.post(`${API_AGENDAMENTO_URL}/sugerir-proximo-dia`, {
            especialistas: pedido_entendido.especialistas,
            data_base: pedido_entendido.data_base,
            periodo_dia: pedido_entendido.periodo_dia
        });

        if (response.data.horarios_encontrados?.length > 0) {
            const dataSugerida = new Date(response.data.pedido_entendido.data_base).toLocaleDateString('pt-BR', {weekday: 'long', day: '2-digit', month: 'long', timeZone: 'UTC'});
            addBotMessage({ text: `Encontrei horários para ${dataSugerida}:`, horarios: response.data.horarios_encontrados });
        } else {
            addBotMessage({ text: "Não consegui encontrar uma data próxima com horários para todos os especialistas solicitados. Por favor, tente com outros especialistas ou uma data diferente." });
            setChatState("AWAITING_REQUEST");
        }
    } catch (error) {
        addBotMessage({ text: "Ocorreu um erro ao sugerir um próximo dia." });
    } finally {
        setIsLoading(false);
    }
  };
  
  const fetchAndDisplaySuggestion = async (pedidoDataTexto: string) => {
    setMessages(prev => prev.map(m => ({ ...m, options: undefined })));
    try {
      const { data } = await axios.post(`${API_EXAMES_URL}/sugerir-horario-otimizado`, { patient_id: patientId, exam_names: selectedExams, pedido_data: pedidoDataTexto });
      const sugestao: SugestaoExame[] = data.sugestao_agendamento;
      if (sugestao?.length > 0) {
        addBotMessage({ text: "Encontrei uma ótima sequência de horários para você:", sugestaoExames: sugestao });
        addBotMessage({ text: "Você gostaria de agendar para esta data e horários?", options: [
          { text: "Sim, agendar", onClick: () => confirmHeuristicSuggestion(sugestao) },
          { text: "Não, quero outras opções", onClick: () => showAlternativeOptions(sugestao, pedidoDataTexto) }
        ]});
        setChatState("SHOWING_HEURISTIC_SUGGESTION");
      }
    } catch (error: any) {
      addBotMessage({ text: error.response?.data?.erro, options: [
        { text: "Ver horários neste dia", onClick: () => switchToManualSelectionFromText(pedidoDataTexto) },
        { text: "Ver dias sugeridos", onClick: () => handleSuggestDays(pedidoDataTexto) },
        { text: "Tentar outra data", onClick: handleTryAnotherDay }
      ]});
    }
  };

  const showAlternativeOptions = (suggestion: SugestaoExame[], pedidoDataTexto: string) => {
    setMessages(prev => prev.map(m => ({ ...m, options: undefined })));
    addBotMessage({
        text: "Sem problemas. O que você prefere?",
        options: [
            { text: "Ver outros horários para este dia", onClick: () => switchToManualSelection(suggestion) },
            { text: "Escolher outra data", onClick: handleTryAnotherDay }
        ]
    });
  };

  const confirmHeuristicSuggestion = (suggestion: SugestaoExame[]) => {
    setMessages(prev =>
      prev.map(msg => {
        if (msg.diasSugeridos) {
          return {
            ...msg,
            diasSugeridos: { ...msg.diasSugeridos, isConfirmed: true },
          };
        }
        return { ...msg, options: undefined };
      })
    );
    setPendingSuggestion(suggestion);
    const dateOfExams = new Date(suggestion[0].horario);
    const formattedDate = dateOfExams.toLocaleDateString('pt-BR', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });
    
    const examDetails = suggestion.map(item => 
        `  - ${item.exame}: ${new Date(item.horario).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
    ).join('\n');

    addBotMessage({ 
      text: `Ótimo! Seu agendamento será para o dia **${formattedDate}** com os seguintes exames e horários:\n${examDetails}\n\nPara finalizar, por favor, informe seu email e CPF (separados por vírgula).`
    });
    setChatState("AWAITING_EXAM_CONFIRMATION_DETAILS");
  };
  
  const handleDaySuggestionConfirmation = (suggestion: SugestaoExame[]) => {
    setMessages(prev =>
      prev.map(msg => {
        if (msg.diasSugeridos) {
          return {
            ...msg,
            diasSugeridos: { ...msg.diasSugeridos, isConfirmed: true },
          };
        }
        return { ...msg, options: undefined };
      })
    );
    confirmHeuristicSuggestion(suggestion);
  };

  const switchToManualSelection = async (suggestion: SugestaoExame[]) => {
    setIsLoading(true);
    setMessages(prev => prev.map(m => ({ ...m, options: undefined })));
    try {
      const date = new Date(suggestion[0].horario);
      const dateStr = date.toISOString().split('T')[0];
      const { data } = await axios.post(`${API_EXAMES_URL}/buscar-todos-horarios`, { exam_names: selectedExams, data: dateStr });
      addBotMessage({ text: "Sem problemas. Aqui estão todos os horários disponíveis:", horariosExames: { date: dateStr, slots: data.horarios_disponiveis } });
      setChatState("AWAITING_MANUAL_EXAM_SELECTION");
    } catch (error) {
      addBotMessage({ text: "Não consegui buscar os horários. Tente novamente mais tarde." });
    } finally {
      setIsLoading(false);
    }
  };

  const switchToManualSelectionFromText = async (pedidoDataTexto: string) => {
    setIsLoading(true);
    setMessages(prev => prev.map(m => ({ ...m, options: undefined })));
    try {
      const { data } = await axios.post(`${API_EXAMES_URL}/buscar-horarios-por-texto`, {
        exam_names: selectedExams,
        pedido_texto: pedidoDataTexto
      });
      addBotMessage({
        text: "Sem problemas. Aqui estão todos os horários disponíveis para o dia que você pediu. Selecione um para cada exame:",
        horariosExames: { date: data.data_entendida, slots: data.horarios_disponiveis }
      });
      setChatState("AWAITING_MANUAL_EXAM_SELECTION");
    } catch (error: any) {
      addBotMessage({ text: error.response?.data?.erro || "Não consegui buscar os horários para a data informada. Tente novamente." });
    } finally {
      setIsLoading(false);
    }
  };

  const handleTryAnotherDay = () => {
    setMessages(prev => prev.map(m => ({ ...m, options: undefined, diasSugeridos: undefined })));
    addBotMessage({ text: "Claro. Para qual outro dia e período você gostaria de verificar?" });
    setChatState("AWAITING_REQUEST");
  };

  const handleSuggestDays = async (pedidoDataTexto: string) => {
    setIsLoading(true);
    setMessages(prev => prev.map(m => ({ ...m, options: undefined })));
    try {
      const { data } = await axios.post(`${API_EXAMES_URL}/sugerir-dias`, { patient_id: patientId, exam_names: selectedExams, pedido_data: pedidoDataTexto });
      if (data.dias_sugeridos?.length > 0) {
        addBotMessage({
          text: "Encontrei estes dias com horários sequenciais disponíveis. Qual você prefere?",
          diasSugeridos: {
            sugestoes: data.dias_sugeridos,
            isConfirmed: false,
          },
        });
        addBotMessage({ text: "Ou, se preferir:", options: [
          { text: "Listar horários do dia original", onClick: () => switchToManualSelectionFromText(pedidoDataTexto) },
          { text: "Digitar outra data", onClick: handleTryAnotherDay }
        ]});
      } else {
        addBotMessage({ text: "Não encontrei outros dias com horários sequenciais disponíveis." });
      }
    } catch (error) {
      addBotMessage({ text: "Não foi possível buscar por dias sugeridos." });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFinalizeManualSelection = (selecoes: Record<string, string>) => {
    setPendingManualSelections(selecoes);
    addBotMessage({ text: `Ok, seleções recebidas. Para finalizar, informe seu email e CPF, separados por vírgula.`});
    setChatState("AWAITING_MANUAL_EXAM_CONFIRMATION_DETAILS");
  };

  const handleSelectSlot = (slot: HorarioResponse) => {
    setSelectedSlots(prev => ({ ...prev, [slot.especialista]: slot }));
  };
  
  const handleFinalize = () => {
    if (Object.keys(selectedSlots).length === 0) return;
    const selections = Object.values(selectedSlots).map(s => `${s.especialista} às ${new Date(s.horario).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`).join(', ');
    addBotMessage({ text: `Confirmar: ${selections}. Informe seu email e CPF.` });
    setChatState("AWAITING_CONFIRMATION_DETAILS");
  };

  return {
    messages, isLoading, input, setInput, chatState, selectedSlots,
    handleSendMessage, handleSelectSlot, handleFinalize, handleStartAgendamento, 
    handleStartSugestao, handleFinalizeManualSelection, confirmHeuristicSuggestion, 
    handleDaySuggestionConfirmation
  };
};