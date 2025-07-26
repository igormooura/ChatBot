export type Message = {
  id: number;
  sender: "user" | "bot";
  timestamp: string;
  text?: string;
  options?: OptionButtonProps[];
  horarios?: HorarioResponse[];
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

export type SelectedAppointment = {
  medico_id: number;
  horario: string;
};

export type ChatState =
  | "INITIAL"
  | "AWAITING_REQUEST"
  | "AWAITING_SUGGESTION_INPUT"
  | "AWAITING_CONFIRMATION_DETAILS"
  | "CONFIRMED";