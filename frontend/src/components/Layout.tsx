import { Outlet, Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Briefcase, Users, Bell, Search, Sparkles, MessageSquare, Settings } from 'lucide-react'

export default function Layout() {
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Jobs', href: '/jobs', icon: Briefcase },
    { name: 'Candidates', href: '/candidates', icon: Users },
    { name: 'Interviews', href: '/interviews', icon: MessageSquare },
    { name: 'Settings', href: '/settings', icon: Settings }, // ✅ AJOUT
  ]

  const isActive = (path: string) => location.pathname.startsWith(path)

  return (
    <div className="min-h-screen relative overflow-hidden" style={{ background: 'linear-gradient(135deg, #F3F2EF 0%, #E8E6E3 100%)' }}>
      
      {/* Decorative Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div 
          className="absolute -top-24 -right-24 w-96 h-96 rounded-full blur-3xl opacity-20"
          style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
        ></div>
        <div 
          className="absolute -bottom-24 -left-24 w-96 h-96 rounded-full blur-3xl opacity-20"
          style={{ background: 'linear-gradient(135deg, #8D6CAB 0%, #E68523 100%)' }}
        ></div>
      </div>

      {/* Modern Floating Header */}
      <header className="sticky top-0 z-50 mx-8 mt-6">
        <div 
          className="backdrop-blur-2xl rounded-3xl border shadow-2xl"
          style={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.7)',
            borderColor: 'rgba(202, 204, 206, 0.3)'
          }}
        >
          <div className="max-w-[1600px] mx-auto px-8">
            <div className="flex items-center justify-between h-20">
              
              {/* Brand with Glow Effect */}
              <div className="flex items-center space-x-8">
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <div 
                      className="w-12 h-12 rounded-2xl flex items-center justify-center shadow-2xl transform transition-transform hover:scale-110 hover:rotate-3"
                      style={{ 
                        background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)'
                      }}
                    >
                      <Sparkles className="w-6 h-6 text-white" strokeWidth={2.5} />
                    </div>
                    <div 
                      className="absolute -inset-1 rounded-2xl blur-lg opacity-50"
                      style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
                    ></div>
                  </div>
                  <div>
                    <h1 
                      className="text-xl font-bold bg-gradient-to-r bg-clip-text text-transparent"
                      style={{ backgroundImage: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
                    >
                      AI Recruitment
                    </h1>
                    <p className="text-xs font-medium" style={{ color: '#888888' }}>Enterprise Platform</p>
                  </div>
                </div>

                {/* Modern Pill Navigation */}
                <nav 
                  className="flex items-center space-x-2 p-1.5 rounded-2xl"
                  style={{ backgroundColor: 'rgba(0, 119, 133, 0.05)' }}
                >
                  {navigation.map((item) => (
                    <Link
                      key={item.name}
                      to={item.href}
                      className="relative flex items-center space-x-2 px-5 py-2.5 rounded-xl font-semibold text-sm transition-all duration-300"
                      style={{
                        backgroundColor: isActive(item.href) ? '#007785' : 'transparent',
                        color: isActive(item.href) ? 'white' : '#888888',
                        boxShadow: isActive(item.href) ? '0 8px 16px rgba(0, 119, 133, 0.3)' : 'none'
                      }}
                    >
                      <item.icon className="w-4 h-4" strokeWidth={2.5} />
                      <span>{item.name}</span>
                    </Link>
                  ))}
                </nav>
              </div>

              {/* Right Actions */}
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <Search 
                    className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4" 
                    style={{ color: '#888888' }}
                  />
                  <input
                    type="text"
                    placeholder="Search anything..."
                    className="w-80 pl-11 pr-4 py-3 rounded-2xl border backdrop-blur-xl text-sm transition-all focus:outline-none focus:ring-4"
                    style={{ 
                      backgroundColor: 'rgba(243, 242, 239, 0.5)',
                      borderColor: 'rgba(202, 204, 206, 0.3)',
                      color: '#313335'
                    }}
                  />
                </div>

                <button 
                  className="relative p-3 rounded-2xl transition-all hover:scale-110"
                  style={{ 
                    backgroundColor: 'rgba(243, 242, 239, 0.5)',
                    color: '#888888'
                  }}
                >
                  <Bell className="w-5 h-5" strokeWidth={2} />
                  <span 
                    className="absolute top-2 right-2 w-2 h-2 rounded-full ring-2 ring-white"
                    style={{ backgroundColor: '#DD5143' }}
                  ></span>
                </button>

                <div className="h-10 w-px" style={{ backgroundColor: 'rgba(202, 204, 206, 0.3)' }}></div>

                <div 
                  className="flex items-center space-x-3 px-4 py-2 rounded-2xl cursor-pointer transition-all hover:scale-105"
                  style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)' }}
                >
                  <div 
                    className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg"
                    style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
                  >
                    <span className="text-white text-sm font-bold">AD</span>
                  </div>
                  <div>
                    <p className="text-sm font-semibold" style={{ color: '#313335' }}>Admin</p>
                    <p className="text-xs" style={{ color: '#888888' }}>Pro Account</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-[1600px] mx-auto px-8 py-8">
        <Outlet />
      </main>
    </div>
  )
}