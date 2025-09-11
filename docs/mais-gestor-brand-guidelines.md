# Mais Gestor - Brand Guidelines & Visual Identity System

**Versão:** 1.0  
**Data:** 08/09/2025  
**Aplicação:** Sistema PapPrefeito e Relatórios Financeiros  

---

## 🎯 Visão Geral da Marca

A **Mais Gestor** posiciona-se como consultoria premium especializada em gestão financeira municipal, com foco em maximização de recursos da saúde pública. A identidade visual deve transmitir:

- **Expertise técnica** e conhecimento especializado
- **Confiabilidade** e profissionalismo executivo  
- **Resultados financeiros** concretos e impactantes
- **Inovação** tecnológica aplicada à gestão pública

---

## 🎨 Sistema de Cores

### Paleta Primária - Confiança & Expertise
```css
/* Azul Corporativo - Elemento principal da marca */
--mais-gestor-primary: #1B4B73;
--mais-gestor-primary-rgb: rgb(27, 75, 115);

/* Azul Accent - Modernidade e tecnologia */
--mais-gestor-accent: #2E86C1; 
--mais-gestor-accent-rgb: rgb(46, 134, 193);
```
**Uso:** Headers, logos, elementos de navegação, dados técnicos

### Paleta Financeira - Impacto & Resultados
```css
/* Verde Sucesso - Crescimento e oportunidades */
--success-green: #27AE60;
--success-green-rgb: rgb(39, 174, 96);

/* Vermelho Alerta - Urgência e perdas */
--alert-red: #E74C3C;
--alert-red-rgb: rgb(231, 76, 60);

/* Dourado Premium - Valor e exclusividade */
--premium-gold: #F39C12;
--premium-gold-rgb: rgb(243, 156, 18);
```
**Uso:** Dados financeiros, call-to-actions, indicadores de performance

### Paleta de Suporte - Neutrals
```css
/* Cinza Executivo - Textos e elementos secundários */
--executive-gray: #34495E;
--executive-gray-rgb: rgb(52, 73, 94);

/* Cinza Claro - Backgrounds e separadores */
--light-gray: #ECF0F1;
--light-gray-rgb: rgb(236, 240, 241);

/* Branco Premium - Clareza e limpeza */
--premium-white: #FFFFFF;
--premium-white-rgb: rgb(255, 255, 255);
```

### Aplicação Estratégica das Cores

| Elemento | Cor | Psicologia | Contexto |
|----------|-----|------------|----------|
| **Ganhos/Oportunidades** | Verde `#27AE60` | Crescimento, sucesso | Cenário "Ótimo", valores positivos |
| **Perdas/Urgência** | Vermelho `#E74C3C` | Alerta, ação necessária | Cenário "Regular", perdas |
| **Marca/Confiança** | Azul `#1B4B73` | Expertise, credibilidade | Headers, logos, dados oficiais |
| **Premium/Valor** | Dourado `#F39C12` | Exclusividade, ROI | CTAs, elementos de valor |

---

## 📝 Sistema Tipográfico

### Hierarquia de Fontes

#### Títulos Principais (H1)
- **Fonte:** Montserrat Bold / Inter Bold
- **Tamanho:** 24-28pt (PDF) / 2.5rem (Web)
- **Cor:** `#1B4B73` (Azul Corporativo)
- **Uso:** "Relatório de Projeção Financeira", títulos de seção

#### Subtítulos (H2)
- **Fonte:** Montserrat SemiBold / Inter SemiBold  
- **Tamanho:** 18-20pt (PDF) / 1.8rem (Web)
- **Cor:** `#34495E` (Cinza Executivo)
- **Uso:** "Cenário Atual", "Considerações Finais"

#### Dados Financeiros (Destaque)
- **Fonte:** Inter Bold / Roboto Mono Bold
- **Tamanho:** 20-24pt (PDF) / 2rem (Web)
- **Cores:** `#27AE60` (positivo) / `#E74C3C` (negativo)
- **Uso:** "R$ 230.388,00", valores de impacto

#### Corpo de Texto (Body)
- **Fonte:** Inter Regular / Open Sans Regular
- **Tamanho:** 11-12pt (PDF) / 1rem (Web)
- **Cor:** `#34495E`
- **Line-height:** 1.4x
- **Uso:** Parágrafos explicativos, descrições

#### Call-to-Action
- **Fonte:** Montserrat Bold
- **Tamanho:** 16-18pt (PDF) / 1.2rem (Web)
- **Cor:** `#FFFFFF` sobre background `#F39C12`
- **Uso:** Botões, CTAs principais

---

## 🔍 Elementos Gráficos & Iconografia

### Sistema de Ícones Estratégicos

| Ícone | Significado | Contexto | Cor |
|-------|-------------|----------|-----|
| 🚀 | Crescimento exponencial | Cenário "Ótimo" | Verde |
| ⚡ | Alta performance | Dados positivos | Azul |
| 🎯 | Precisão estratégica | Análises técnicas | Azul |
| 💎 | Premium/Valor | Serviços Mais Gestor | Dourado |
| ⚠️ | Alerta/Urgência | Oportunidades perdidas | Vermelho |
| 📈 | Crescimento/Tendência | Projeções futuras | Verde |
| 🏆 | Excelência | Classificação "Ótimo" | Dourado |
| 📊 | Análise de dados | Relatórios, gráficos | Azul |

### Elementos Visuais Distintivos

#### Gradientes
```css
/* Gradiente Corporativo - Headers */
background: linear-gradient(135deg, #1B4B73 0%, #2E86C1 100%);

/* Gradiente Premium - CTAs */
background: linear-gradient(135deg, #27AE60 0%, #F39C12 100%);

/* Gradiente Sutil - Cards */
background: linear-gradient(180deg, #FFFFFF 0%, #ECF0F1 100%);
```

#### Sombras & Profundidade
```css
/* Sombra Suave - Cards */
box-shadow: 0 2px 8px rgba(27, 75, 115, 0.1);

/* Sombra Premium - CTAs */
box-shadow: 0 4px 16px rgba(243, 156, 18, 0.3);

/* Sombra Executiva - Headers */
box-shadow: 0 2px 12px rgba(52, 73, 94, 0.15);
```

#### Bordas & Geometria
```css
/* Radius Moderno */
border-radius: 8px; /* Cards padrão */
border-radius: 12px; /* Elementos premium */
border-radius: 24px; /* Botões CTA */

/* Borders Sutis */
border: 1px solid #ECF0F1; /* Separadores */
border: 2px solid #2E86C1; /* Elementos ativos */
```

---

## 📐 Layout & Composição

### Grid System
- **Container máximo:** 1200px
- **Gutter:** 24px
- **Breakpoints:** Mobile-first approach
- **Alinhamento:** Centrado com margens consistentes

### Espaçamento (Spacing Scale)
```css
--space-xs: 4px;   /* 0.25rem */
--space-sm: 8px;   /* 0.5rem */
--space-md: 16px;  /* 1rem */
--space-lg: 24px;  /* 1.5rem */
--space-xl: 32px;  /* 2rem */
--space-xxl: 48px; /* 3rem */
```

### Composição Visual

#### Regra de Hierarquia
1. **Impacto financeiro** (maior destaque)
2. **Marca Mais Gestor** (segundo destaque) 
3. **Dados técnicos** (terceiro destaque)
4. **Texto explicativo** (suporte)

#### Proporções Áurea
- **Logo:** 16:9 ou 3:2 ratio
- **Cards:** 4:3 ratio
- **Headers:** 21:9 ratio (wide)

---

## 🖼️ Templates & Layouts

### Template PDF - Relatório Financeiro

#### Página 1: Capa Premium
```
┌─────────────────────────────────────────────────────────────┐
│ [Gradiente azul diagonal]                                   │
│  [LOGO MAIS GESTOR - 3x tamanho]                    🎯     │
│                                                             │
│  RELATÓRIO DE OPORTUNIDADES FINANCEIRAS                   │
│  Município de [NOME]                    [Montserrat Bold]  │
│                                                             │
│  💰 POTENCIAL DE IMPACTO:              [Card dourado]      │
│     R$ X,XX MILHÕES ANUAIS                                │
│                                                             │
│  📊 [Gráfico minimalista da oportunidade]                 │
│                                                             │
│  🌐 maisgestor.com.br                  [Dourado]          │
└─────────────────────────────────────────────────────────────┘
```

#### Páginas Internas: Conteúdo Técnico
```
┌─────────────────────────────────────────────────────────────┐
│ [Header azul] MAIS GESTOR | Título da Seção               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ [Card principal com sombra]                                │
│   Conteúdo técnico formatado                              │
│                                                             │
│ [Sidebar visual]  [Gráficos com paleta personalizada]     │
│  Progress       │                                          │
│  Indicators     │  Dados financeiros destacados           │
│                 │                                          │
└─────────────────────────────────────────────────────────────┘
```

#### Página Final: Call-to-Action Premium
```
┌─────────────────────────────────────────────────────────────┐
│ [Gradiente verde-dourado]                                   │
│                                                             │
│  🚀 MAXIMIZE SEU POTENCIAL FINANCEIRO NA SAÚDE            │
│                                                             │
│     "R$ X,XX MILHÕES em diferença anual                   │
│      cada indicador importa!"                             │
│                                                             │
│  ▼ PRÓXIMOS PASSOS COM A MAIS GESTOR:                     │
│  ✓ Item 1    ✓ Item 2    ✓ Item 3    ✓ Item 4            │
│                                                             │
│     [BOTÃO DOURADO] AGENDE SUA CONSULTORIA                │
│                                                             │
│  [QR Code] www.maisgestor.com.br [Contatos múltiplos]     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📱 Responsividade & Adaptação

### Breakpoints
```css
/* Mobile First */
--mobile: 320px;
--tablet: 768px;  
--desktop: 1024px;
--wide: 1440px;
```

### Adaptações por Dispositivo
- **Mobile:** Logo reduzido, single column, CTAs ampliados
- **Tablet:** Two columns, navegação lateral
- **Desktop:** Full layout, sidebar fixa, hover states
- **Print/PDF:** Cores CMYK, fontes embarcadas, otimização de tamanho

---

## ✅ Checklist de Aplicação

### Elementos Obrigatórios
- [ ] Logo Mais Gestor visível e bem posicionado
- [ ] Paleta de cores aplicada consistentemente
- [ ] Tipografia hierarquizada corretamente
- [ ] Call-to-action clara e destacada
- [ ] Informações de contato (maisgestor.com.br)
- [ ] Elementos de urgência/oportunidade
- [ ] Dados financeiros em destaque
- [ ] Ícones estratégicos aplicados

### Qualidade Visual
- [ ] Contraste adequado para legibilidade
- [ ] Alinhamento perfeito de elementos
- [ ] Espaçamento consistente
- [ ] Imagens em alta resolução
- [ ] Cores reproduzidas fielmente

### Performance
- [ ] Carregamento otimizado
- [ ] Tamanho de arquivo controlado
- [ ] Compatibilidade entre browsers/viewers
- [ ] Impressão mantém qualidade

---

## 🔗 Recursos & Assets

### Downloads
- **Paleta de cores:** `mais-gestor-colors.ase`
- **Fontes:** Montserrat, Inter (Google Fonts)
- **Logos:** `mais-gestor-logo-kit.zip`
- **Ícones:** `mais-gestor-icons.svg`
- **Templates:** `pdf-templates/`

### Links Úteis
- **Site oficial:** https://maisgestor.com.br
- **Fontes:** https://fonts.google.com
- **Ícones:** https://heroicons.com

---

## 📞 Contato & Suporte

**Responsável pela marca:** Alysson Ribeiro  
**Email:** contato@maisgestor.com.br  
**Última revisão:** 08/09/2025  

---

*Este documento serve como guia oficial para implementação da identidade visual da Mais Gestor em todos os materiais de comunicação, relatórios e interfaces digitais.*