// src/pages/Home.tsx
import Header from "../components/Header/Header";
import HeroSection from "../components/HeroSection/HeroSection";
import Footer from "../components/Footer/Footer";
import Background from "../components/Background/Background";

const Home = () => {
  return (
    <Background>
      <Header />
      <HeroSection />
      <Footer />
    </Background>
  );
};

export default Home;
