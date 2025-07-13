import { BrowserRouter, Route, Routes } from "react-router-dom"
import Home from "./pages/Home"
import { Userpage } from "./pages/UserPage"
import { AdminPage } from "./pages/AdminPage"
import LoginPage from "./pages/LoginPage"

function App() {
  return (
    <BrowserRouter>
    <Routes>
      <Route path='/' element={<Home/>}/>
      <Route path='/user' element={<Userpage/>}/>
      <Route path='/admin' element={<AdminPage/>}/>
      <Route path='/login' element={<LoginPage/>}/>
    </Routes>
    </BrowserRouter>
  )
}

export default App
