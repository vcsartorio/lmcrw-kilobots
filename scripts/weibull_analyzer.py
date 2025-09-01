import numpy as np
import scipy.special as sc
from scipy.optimize import curve_fit
import warnings
import matplotlib.pyplot as plt

# Para um código mais limpo, coloquei os métodos dentro de uma classe
class WeibullFPTAnalyzer:
    def __init__(self, discovery_robots_values, discovery_time=None):
        self.discovery_robots_values = discovery_robots_values
        self.discovery_time = np.mean(discovery_robots_values) if discovery_time is None else discovery_time
        self.iteration_history = []
        self.times_value = None
        self.F_empirical = None

    def estimatorKM(self, data, censored):
        # Versão mais eficiente e numericamente estável do Kaplan-Meier
        n_individuals = data.size + censored
        # np.unique lida com múltiplos robôs encontrando o alvo no mesmo instante de tempo
        times, event_counts = np.unique(data, return_counts=True)
        
        at_risk = np.array([n_individuals - np.sum(event_counts[:i]) for i in range(len(event_counts))])
        
        survival_prob = np.cumprod((at_risk - event_counts) / at_risk)
        
        # Precisamos mapear as probabilidades de volta para o array 'data' original
        # que pode ter tempos duplicados.
        prob_map = {t: p for t, p in zip(times, survival_prob)}
        full_survival_prob = np.array([prob_map[t] for t in data])

        F = 1 - full_survival_prob.reshape(-1, 1)
        return F

    def weib_cdf(self, x, alpha, gamma):
        return (1 - np.exp(-np.power(x / alpha, gamma)))

    def calculateWeibullDiscoveryTime(self, max_simulation_time):
        self.iteration_history = []
        fpt = np.asarray(self.discovery_robots_values)
        censored = fpt.size - np.count_nonzero(fpt)
        if censored == 0:
            print("Nenhum dado censurado. Retornando média simples.")
            return self.discovery_time

        fpt_sorted = np.sort(fpt)
        self.times_value = fpt_sorted[censored:]

        # Se não houver eventos, não podemos calcular.
        if self.times_value.size == 0:
            print("AVISO: Nenhum robô encontrou o alvo. Não é possível calcular a média.")
            return np.nan

        self.F_empirical = self.estimatorKM(self.times_value, censored)

        # --- Início da Lógica Heurística para o bound_is ---
        kilobot_tick_per_seconds = 32
        bound_is = max_simulation_time*kilobot_tick_per_seconds
        max_iterations = 10
        target_ratio = 0.63

        print("Iniciando ajuste heurístico do bound_is...")
        print(f"Discovery time: {self.times_value.mean():.2f}")
        print(f"Fraction Discovery: {len(self.times_value) / len(self.discovery_robots_values):.2%}")
        for i in range(max_iterations):
            print(f"\n--- Iteração {i + 1}/{max_iterations} ---")
            print(f"Usando bound_is: {bound_is:.2f}")
            
            popt_weibull = None
            try:
                # Adicionado bounds inferiores para evitar valores zero, que causam erros
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore") # Ignora avisos de otimização que não são críticos
                    popt_weibull, _ = curve_fit(
                        self.weib_cdf,
                        xdata=self.times_value,
                        ydata=np.squeeze(self.F_empirical),
                        bounds=([1e-9, 1e-9], [bound_is, 10]), # Bounds para [alpha, gamma]
                        method='trf'
                    )
            except RuntimeError as e:
                print(f"Erro no curve_fit: {e}. O bound pode ser muito restritivo. Interrompendo.")
                return np.nan # Retorna um valor que indica falha

            alpha, gamma = popt_weibull
            current_ratio = alpha / bound_is

            self.iteration_history.append({'bound': bound_is, 'alpha': alpha, 'gamma': gamma})

            print(f"Alpha ajustado: {alpha:.2f}")
            print(f"Ratio (Alpha / Bound): {current_ratio:.2%}")

            mean = sc.gamma(1 + (1. / gamma)) * alpha
            std_dev = np.sqrt(alpha ** 2 * sc.gamma(1 + (2. / gamma)) - mean ** 2)
            std_error = std_dev / np.sqrt(self.times_value.size)
            print(f"Mean Weibull: {mean:.2f}")

            # Condição de parada: o alpha ocupa 63% ou menos do espaço de busca
            if current_ratio <= target_ratio+0.01:
                print(f"\nCondição satisfeita ({current_ratio:.2%} <= {target_ratio:.2%}). Parando o ajuste.")
                break
            else:
                # Se não satisfeito, calcula o próximo bound_is
                print(f"Condição não satisfeita. Recalculando bound_is para a próxima iteração...")
                # Aumento proporcional: O novo limite é calculado para que o alpha ATUAL
                # fique exatamente na marca do target_ratio.
                bound_is = alpha / target_ratio
                
                if i == max_iterations - 1:
                    print("\nAVISO: Número máximo de iterações atingido sem satisfazer a condição.")
                    print("O resultado pode não ser estável. Considere rodar a simulação por mais tempo.")
        
        # --- Fim da Lógica Heurística ---

        print("\n--- Resultado Final do Ajuste ---")
        final_params = self.iteration_history[-1]
        alpha, gamma = final_params['alpha'], final_params['gamma']
        print(f"Alpha final: {alpha:.2f} - Gamma final: {gamma:.2f}")

        mean = sc.gamma(1 + (1. / gamma)) * alpha
        std_dev = np.sqrt(alpha ** 2 * sc.gamma(1 + (2. / gamma)) - mean ** 2)
        std_error = std_dev / np.sqrt(self.times_value.size)

        print(f"\nMean Weibull: {mean:.2f}")
        return mean
    
    def plot_iterations(self):
        """
        Plota os dados empíricos (Kaplan-Meier) e a curva de Weibull ajustada
        para cada iteração do processo heurístico.
        """
        if not self.iteration_history or self.times_value is None:
            print("Execute 'calculateWeibullDiscoveryTime' primeiro para gerar os dados.")
            return

        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(12, 8))

        # 1. Plota os dados dos robôs (resultado do Kaplan-Meier)
        ax.plot(self.times_value, self.F_empirical, 'o', color='black', markersize=6, label='Dados Empíricos (Kaplan-Meier)')

        # 2. Plota a curva de Weibull de cada iteração
        # Define o eixo X para as curvas, indo um pouco além do último bound para uma boa visualização
        final_bound = self.iteration_history[-1]['bound']
        x_curve = np.linspace(0, final_bound * 1.1, 500)

        for i, history in enumerate(self.iteration_history):
            alpha = history['alpha']
            gamma = history['gamma']
            y_curve = self.weib_cdf(x_curve, alpha, gamma)
            ax.plot(x_curve, y_curve, label=f'Iteração {i+1} (α={alpha:.2f})', linewidth=2.5, alpha=0.7)

        # 3. Embelezamento do gráfico
        ax.set_title('Ajuste Iterativo da Curva de Weibull aos Dados Empíricos', fontsize=16)
        ax.set_xlabel('Tempo de Descoberta (passos)', fontsize=12)
        ax.set_ylabel('Probabilidade Cumulativa (CDF)', fontsize=12)
        ax.legend(title='Legenda', fontsize=10)
        ax.set_xlim(0, x_curve.max())
        ax.set_ylim(0, 1.05)

        plt.show()
    

# Exemplo de uso com dados simulados

#### Cenário 3: Valores reais para 80 robos e simulation_time: 3k
simulation_time = 3000
dados_selecionados = np.array([
    73005, 0, 0, 19877, 0, 0, 0, 0, 0, 59972, 0, 0, 4563, 15227, 2052, 0, 61094, 0, 0, 0, 0, 0, 0, 6113, 0, 0, 0, 0, 0, 30014, 0, 47684, 0, 0, 0, 0, 0, 0, 25333, 57418, 0, 0, 6361, 0, 0, 52861, 0, 0, 61026, 0, 0, 0, 0, 0, 60124, 0, 0, 0, 0, 61132, 72912, 0, 0, 0, 0, 65592, 5316, 0, 0, 0, 0, 0, 316, 0, 0, 0, 0, 595, 0, 0
])
# dados_selecionados = np.array([
#     0, 0, 0, 82212, 0, 0, 0, 36573, 0, 1618, 25940, 0, 80910, 0, 36728, 11699, 34899, 24939, 0, 0, 0, 0, 46431, 0, 41645, 15199, 0, 0, 0, 0, 62018, 0, 2737, 19161, 0, 8779, 31682, 0, 0, 0, 0, 34682, 0, 0, 4383, 64368, 37, 14579, 0, 58590, 0, 51770, 0, 502, 0, 20004, 36508, 0, 35070, 15093, 0, 37, 8655, 0, 26477, 0, 50954, 24496, 502, 0, 0, 8965, 81065, 51763, 15713, 13928, 11448, 0, 59287, 0
# ])
analisador = WeibullFPTAnalyzer(dados_selecionados)
media = analisador.calculateWeibullDiscoveryTime(simulation_time)
print(f"\nMédia final para o Cenário 1: {media:.2f}")
analisador.plot_iterations()

# print("\n" + "="*50 + "\n")

### Cenário 1: Bound inicial é suficiente
### 15 de 20 robôs encontram o alvo, tempos baixos
# dados_cenario = np.array([150000, 610000, 450000, 0, 52000, 480000, 0, 0, 550000, 263000, 0, 0, 580000, 0, 47000, 353000, 56000, 159000, 0, 60000])
# analisador = WeibullFPTAnalyzer(dados_cenario)
# media = analisador.calculateWeibullDiscoveryTime(12000)
# print(f"\nMédia final para o Cenário 1: {media:.2f}")
# analisador.plot_iterations()

# print("\n" + "="*50 + "\n")

# ### Cenário 2: Heurística será acionada
# ### 16 de 20 robôs encontram o alvo, mas os tempos são muito maiores
# dados_cenario = np.array([80000, 95000, 120000, 0, 78000, 110000, 0, 0, 99000, 130000, 82000, 85000, 115000, 0, 88000, 92000, 105000, 108000, 0, 100000])
# analisador = WeibullFPTAnalyzer(dados_cenario)
# media = analisador.calculateWeibullDiscoveryTime(3000)
# print(f"\nMédia final para o Cenário 2: {media:.2f}")
# analisador.plot_iterations()