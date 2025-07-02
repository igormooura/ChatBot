import Footer from "../components/Footer/Footer";
import Header from "../components/Header/Header";
import HeroSection from "../components/HeroSection/HeroSection";

const Home = () => {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow">
        <HeroSection />
      </main>
      <Footer />
    </div>
  );
};

export default Home;
