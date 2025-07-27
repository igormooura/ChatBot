export type Message = {
  id: number;
  sender: "user" | "bot";
  timestamp: string;
  text?: string;
  options?: OptionButtonProps[];
  horarios?: HorarioResponse[];
  upload?: { onFileUpload: (file: File) => void };
  examSelector?: {
    exams: string[];
    onSelectionChange: (selected: string[]) => void;
  };
  sugestaoExames?: SugestaoExame[];
  horariosExames?: {
    date: string;
    slots: Record<string, string[]>;
  };
  // ✅ CORRIGIDO: A função onConfirm foi removida daqui.
  diasSugeridos?: {
    sugestoes: SugestaoExame[][];
    isConfirmed: boolean;
  };
};

export type OptionButtonProps = {
  text: string;
  onClick: () => void;
};

export type HorarioResponse = {
  especialista: string;
  medico_id: number;
  medico_nome: string;
  horario: string;
};

export type SugestaoExame = {
  exame: string;
  horario: string;
};

export type ChatState =
  | "INITIAL"
  | "AWAITING_REQUEST"
  | "AWAITING_SUGGESTION_INPUT"
  | "AWAITING_CONFIRMATION_DETAILS"
  | "AWAITING_EXAM_CONFIRMATION_DETAILS"
  | "AWAITING_MANUAL_EXAM_CONFIRMATION_DETAILS"
  | "CONFIRMED"
  | "AWAITING_EXAM_PDF"
  | "AWAITING_EXAM_SELECTION_AND_DATE"
  | "SHOWING_HEURISTIC_SUGGESTION"
  | "AWAITING_MANUAL_EXAM_SELECTION";