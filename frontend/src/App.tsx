import { BrowserRouter, Route, Routes } from "react-router-dom"
import Home from "./pages/Home"
import UserPage from "./pages/UserPage";
import { AdminPage } from "./pages/AdminPage"
import LoginPage from "./pages/LoginPage"
import ChatPage from "./pages/ChatPage"


function App() {
  return (
    <BrowserRouter>
    <Routes>
      <Route path='/' element={<Home/>}/>
      <Route path='/user' element={<UserPage/>}/>
      <Route path='/admin' element={<AdminPage/>}/>
      <Route path='/login' element={<LoginPage/>}/>
      <Route path='/chatbot' element={<ChatPage/>}/>
    </Routes>
    </BrowserRouter>
  )
}

export default App
