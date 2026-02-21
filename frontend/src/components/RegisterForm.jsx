import LoginForm from './LoginForm'

// Reuse LoginForm component since it handles both login and registration
const RegisterForm = () => {
  return <LoginForm />
}

export default RegisterForm