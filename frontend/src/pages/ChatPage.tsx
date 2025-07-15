import Background from "../components/Background/Background";
import ChatMessage from "../components/Chat/ChatMessage";
import Header from "../components/Header/Header";
import ChatContainer from "../components/Chat/ChatContainer";

type Message = { 
  id: number;
  sender: "user" | "bot";
  text: string;
  timestamp: string;
};

const sampleMessages: Message[] = [ //temporário
  {
    id: 1,
    sender: "user",
    text: "Oi, tudo bem?",
    timestamp: "2025-07-15T19:05:00-03:00",
  },
  {
    id: 2,
    sender: "bot",
    text: "Olá! Tudo ótimo e com você?",
    timestamp: "2025-07-15T19:05:05-03:00",
  },
];;

const ChatPage = () => {
  return (
    <Background>
      <Header />
      <div className="flex justify-center">
        <ChatContainer>
          {sampleMessages.map((msg) => (
            <ChatMessage key={msg.id} messages={msg} />
          ))}
        </ChatContainer>
      </div>
    </Background>
  );
};

export default ChatPage;
