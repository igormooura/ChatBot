import { BrowserRouter, Route, Routes } from "react-router-dom"
import Home from "./pages/Home"
import { Userpage } from "./pages/UserPage"
import { AdminPage } from "./pages/AdminPage"

function App() {
  return (
    <BrowserRouter>
    <Routes>
      <Route path='/' element={<Home/>}/>
      <Route path='/user' element={<Userpage/>}/>
      <Route path='/admin' element={<AdminPage/>}/>
    </Routes>
    </BrowserRouter>
  )
}

export default App
