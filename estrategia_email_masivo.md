# 📧 **GUÍA COMPLETA PARA ENVÍO MASIVO SIN BLACKLIST**

## 🎯 **REGLA DE ORO: CALENTAMIENTO DE DOMINIO**

**NUNCA envíes 1000 emails el día 1. NUNCA.**

```php
// Calendario de calentamiento (30 días)
$warmupSchedule = [
    'Semana 1' => ['día' => 10-20, 'total' => 100],
    'Semana 2' => ['día' => 30-50, 'total' => 250],
    'Semana 3' => ['día' => 75-100, 'total' => 500],
    'Semana 4' => ['día' => 150-200, 'total' => 1000],
    'Mes 2+'   => ['día' => 300-500, 'total' => 'ilimitado']
];
```

---

## 🔧 **CONFIGURACIÓN TÉCNICA OBLIGATORIA**

### **1. SPF (Sender Policy Framework)**
```dns
TXT @ "v=spf1 ip4:TU_IP include:_spf.google.com ~all"
```

### **2. DKIM (DomainKeys Identified Mail)**
```dns
TXT google._domainkey "v=DKIM1; k=rsa; p=MIGfMA0GCS..."
```

### **3. DMARC (Domain-based Message Authentication)**
```dns
TXT _dmarc "v=DMARC1; p=quarantine; rua=mailto:admin@tudominio.com"
```

### **4. rDNS (Reverse DNS)**
- Tu IP debe resolver a tu dominio
- Contacta a tu hosting para configurarlo

### **5. Dominio dedicado para outreach**
```
Dominio principal: tuagencia.com
Dominio envíos: contacto-tuagencia.com
```

**Por qué:** Si te queman, no afecta tu dominio principal

---

## 📨 **ESTRATEGIA DE ENVÍO INTELIGENTE**

### **MÉTODO 1: SUBDOMINIOS ROTATIVOS**

```php
class EmailSender {
    private $subdomains = [
        'contact.tuagencia.com',
        'hello.tuagencia.com',
        'team.tuagencia.com',
        'info.tuagencia.com'
    ];
    
    private $dailyLimit = [
        'gmail.com' => 50,      // Gmail es estricto
        'hotmail.com' => 75,    // Hotmail medio
        'yahoo.com' => 100,     // Yahoo más relajado
        'corporativo' => 30     // Dominios corporativos, cuidado
    ];
    
    public function sendBatch($emails) {
        // Agrupar por dominio receptor
        $grouped = $this->groupByDomain($emails);
        
        foreach($grouped as $domain => $recipients) {
            $limit = $this->dailyLimit[$domain] ?? 30;
            
            foreach(array_chunk($recipients, $limit) as $batch) {
                $this->sendWithRotation($batch);
                sleep(rand(300, 600)); // 5-10 min entre batches
            }
        }
    }
}
```

---

## 🎭 **TÉCNICAS ANTI-SPAM AVANZADAS**

### **1. SPINTAX (Variación de contenido)**

```php
$spintax = "
{Hola|Buenos días|Saludos} {nombre},

{Vi|Encontré|Noté} que tu {empresa|negocio|compañía} 
{no tiene|no cuenta con|carece de} {presencia digital|página web|marketing online}.

{Podemos ayudarte|Te podemos apoyar|Queremos ayudarte} a 
{crecer|aumentar ventas|conseguir más clientes}.

{Saludos|Atentamente|Cordialmente},
{Juan|El equipo|Marketing}
";

function spinText($text) {
    return preg_replace_callback(
        '/{([^}]+)}/',
        function($matches) {
            $options = explode('|', $matches[1]);
            return $options[array_rand($options)];
        },
        $text
    );
}
```

### **2. PERSONALIZACIÓN REAL**

```php
$template = "
Hola {nombre},

Vi que {empresa} está en {distrito} y se dedica a {rubro}.

Específicamente noté que:
{problema_especifico}

Hemos ayudado a negocios similares como {cliente_similar} a {resultado}.

¿Te interesa una llamada de 10 minutos el {dia_propuesto}?
";

// NUNCA uses "querido cliente" o templates genéricos
```

### **3. LINKS INTELIGENTES**

```php
// MAL: 20 personas, mismo link
$link = "https://tuagencia.com/landing";

// BIEN: Links únicos trackeable
$link = "https://tuagencia.com/l/" . base64_encode($email);

// MEJOR: Sin links en primer email
$firstEmail = "Sin links, solo texto";
$secondEmail = "Si responden, ahí sí link";
```

---

## 🚀 **SERVICIOS DE ENVÍO RECOMENDADOS**

### **TIER 1: Para Cold Email (Especializados)**

**1. Lemlist** 
- $29/mes
- Calentamiento automático
- Detección de spam score

**2. Woodpecker**
- $40/mes  
- Follow-ups automáticos
- Rotación de emails

**3. SendGrid** (Free tier)
- 100 emails/día gratis
- API robusta
- Buena reputación

### **TIER 2: SMTP Propio**

```php
// Configurar múltiples SMTP
$smtpServers = [
    [
        'host' => 'smtp.gmail.com',
        'user' => 'cuenta1@gmail.com',
        'pass' => 'app-specific-password',
        'limit' => 500, // por día
        'port' => 587
    ],
    [
        'host' => 'smtp.sendinblue.com',
        'user' => 'cuenta@tudominio.com',
        'pass' => 'api-key',
        'limit' => 300,
        'port' => 587
    ]
];
```

---

## 📊 **MONITOREO Y MÉTRICAS**

### **Herramientas de monitoreo GRATIS:**

```php
// 1. Check Spam Score
$tools = [
    'mail-tester.com',       // 3 tests gratis/día
    'spamcheck.postmarkapp.com',
    'mxtoolbox.com/blacklists'
];

// 2. Verificar blacklists
function checkBlacklist($ip) {
    $blacklists = [
        'zen.spamhaus.org',
        'bl.spamcop.net',
        'b.barracudacentral.org'
    ];
    
    foreach($blacklists as $bl) {
        $reverse_ip = implode('.', array_reverse(explode('.', $ip)));
        $check = $reverse_ip . '.' . $bl;
        
        if(gethostbyname($check) != $check) {
            return "BLACKLISTED en $bl";
        }
    }
    return "CLEAN";
}
```

---

## 🎯 **ESTRATEGIA DE CONTENIDO QUE NO TRIGGEREA SPAM**

### **EVITA estas palabras:**
```php
$spamWords = [
    'gratis', 'free', '100%',
    'garantizado', 'urgente',
    'oferta', 'promoción',
    'click aquí', 'compre ahora',
    '$$', '!!!', 'MAYÚSCULAS'
];
```

### **USA este formato:**
```
Asunto: Pregunta sobre {empresa}
Asunto: {nombre}, pregunta rápida
Asunto: Idea para {problema específico}

NUNCA:
- "Oferta especial"
- "No te pierdas esto"
- "Última oportunidad"
```

---

## 🔄 **SISTEMA DE FOLLOW-UP AUTOMÁTICO**

```php
class FollowUpSystem {
    
    private $sequence = [
        1 => ['días' => 0, 'template' => 'initial'],
        2 => ['días' => 3, 'template' => 'follow1'],
        3 => ['días' => 7, 'template' => 'follow2'],
        4 => ['días' => 14, 'template' => 'break_up']
    ];
    
    public function getTemplate($step, $data) {
        $templates = [
            'initial' => "Hola {nombre}, vi que {problema}...",
            
            'follow1' => "Hola {nombre}, ¿pudiste ver mi email anterior?",
            
            'follow2' => "{nombre}, solo quería saber si esto es prioridad ahora",
            
            'break_up' => "Último intento - ¿debo asumir que no hay interés?"
        ];
        
        return $this->personalize($templates[$step], $data);
    }
}
```

---

## 💡 **HACK: INBOX WARMING CON EMPLEADOS**

```php
// Antes de enviar a clientes, "calienta" tu dominio

$warmupStrategy = [
    'Semana 1' => [
        'Enviar emails entre cuentas propias',
        'Empleados responden y marcan "no spam"',
        'Mover a "Principal" en Gmail'
    ],
    'Semana 2' => [
        'Emails a partners/amigos',
        'Pedir que respondan',
        'Conversaciones reales'
    ],
    'Semana 3' => [
        'Primeros cold emails',
        'Solo 10-20 por día',
        'A los leads más probables'
    ]
];
```

---

## 🛡️ **PLAN B: CUANDO TE BLOQUEAN**

### **Si Gmail te marca spam:**
1. Reduce envíos 90%
2. Solo emails respondidos por 1 semana
3. Pide a contactos que te saquen de spam
4. Cambia contenido completamente

### **Si entras en blacklist:**
```php
// 1. Identificar cuál blacklist
$blacklistCheck = "mxtoolbox.com/blacklists";

// 2. Solicitar removal
$removalProcess = [
    'Spamhaus' => 'Formulario online, 24-48h',
    'Barracuda' => 'Portal removal, instantáneo',
    'SpamCop' => 'Automático en 24h'
];

// 3. Mientras tanto, usar dominio backup
```

---

## 📈 **MÉTRICAS A MONITOREAR**

```php
class EmailMetrics {
    
    public function track() {
        return [
            'open_rate' => '> 20% es bueno',
            'reply_rate' => '> 5% excelente',
            'bounce_rate' => '< 3% obligatorio',
            'spam_rate' => '< 0.1% crítico',
            'unsubscribe' => '< 2% saludable'
        ];
    }
    
    public function danger_signals() {
        return [
            'Opens < 10%' => 'Vas a spam folder',
            'Bounces > 5%' => 'Lista desactualizada',
            'Spam reports > 0.5%' => 'PARA TODO',
            'No replies en 100 envíos' => 'Mensaje malo'
        ];
    }
}
```

---

## 🚦 **WORKFLOW COMPLETO SEGURO**

### **MES 1: Setup**
```
Día 1-7: Configurar SPF/DKIM/DMARC
Día 8-14: Warming con equipo interno
Día 15-21: 10 emails/día a leads warm
Día 22-30: 25 emails/día, medir métricas
```

### **MES 2: Escalamiento**
```
Semana 1: 50 emails/día
Semana 2: 100 emails/día
Semana 3: 150 emails/día
Semana 4: 200 emails/día
```

### **MES 3+: Optimización**
```
- A/B testing subjects
- Segmentación por industria
- Follow-ups automáticos
- 300-500 emails/día
```

---

## 💰 **SETUP ECONÓMICO RECOMENDADO**

```php
$budget_setup = [
    'Dominio nuevo' => '$10/año',
    'Google Workspace' => '$6/mes (1 cuenta)',
    'SendinBlue' => 'Free (300/día)',
    'Warming service' => '$15/mes opcional',
    'Total' => '< $25/mes'
];

$herramientas_gratis = [
    'Mail-tester.com' => 'Check spam score',
    'MXToolbox' => 'Blacklist check',
    'Google Postmaster' => 'Reputación en Gmail',
    'Warmup Inbox' => 'Free trial 7 días'
];
```

---

## ⚠️ **ERRORES FATALES A EVITAR**

```
❌ Comprar lista de emails
❌ Enviar 1000 emails día 1
❌ Usar solo 1 template
❌ No limpiar bounces
❌ Ignorar unsubscribes
❌ Links acortados (bit.ly)
❌ Adjuntos en primer email
❌ IPs compartidas baratas
```

## 📧 **ESTRATEGIAS AVANZADAS PARA CONSEGUIR EMAILS DE NEGOCIOS**

### **🎯 MÉTODO 1: PATTERN MATCHING (90% efectividad)**

**La mayoría de empresas usan patrones predecibles:**

```php
$patterns = [
    '{nombre}@{dominio}',           // juan@empresa.com
    '{n}.{apellido}@{dominio}',     // j.perez@empresa.com
    '{nombre}.{apellido}@{dominio}', // juan.perez@empresa.com
    '{nombre}{apellido}@{dominio}',  // juanperez@empresa.com
    'info@{dominio}',
    'ventas@{dominio}',
    'contacto@{dominio}',
    'administracion@{dominio}'
];
```

---

### **🔍 MÉTODO 2: HUNTER.IO GRATIS (Hack)**

**Sin pagar, puedes:**
- Ver el patrón de email (ej: {f}.{last}@company.com)
- Verificar si un email existe
- 25 búsquedas gratis/mes

**Truco:** Crear múltiples cuentas con emails temporales = búsquedas ilimitadas

---

### **🌐 MÉTODO 3: WEBSITE SCRAPING INTELIGENTE**

```php
$urlsToCheck = [
    '/contacto', '/contactenos', '/contact',
    '/nosotros', '/about', '/about-us',
    '/equipo', '/team', '/staff',
    '/terminos', '/terms', '/privacy',
    '/ayuda', '/help', '/support'
];

// Regex mejorado para emails:
$patterns = [
    '/[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/i',
    '/[a-z0-9._%+-]+\[@\][a-z0-9.-]+\.[a-z]{2,}/i', // con escape
    '/[a-z0-9._%+-]+\(at\)[a-z0-9.-]+\.[a-z]{2,}/i', // (at)
    '/[a-z0-9._%+-]+\[at\][a-z0-9.-]+\.[a-z]{2,}/i', // [at]
];
```

---

### **📱 MÉTODO 4: WHATSAPP BUSINESS API**

Muchos negocios tienen WhatsApp Business con email público. 
**Hack:** Enviar mensaje pidiendo cotización, auto-respuesta suele tener email

---

### **🔗 MÉTODO 5: LINKEDIN SALES NAVIGATOR (Sin pagar)**

```javascript
// LinkedIn expone emails en el código fuente
"emailAddress":"xxx@company.com"
"contactInfo":{"emailAddress":"xxx@company.com"}
```

---

### **🎭 MÉTODO 7: GOOGLE DORKING ESPECÍFICO**

```bash
# Email específico de una empresa
site:empresa.pe "@" 
site:empresa.pe "email" OR "correo"
"empresa.pe" "@gmail.com" OR "@hotmail.com"

# Encontrar empleados y sus emails
site:linkedin.com "empresa" "@"
"empresa" filetype:pdf "@"
```

---

### **💼 MÉTODO 8: HERRAMIENTAS "FREEMIUM" ABUSABLES**

1. **Clearbit Connect**: 100 emails/mes gratis
2. **Snov.io**: 50 créditos gratis/mes
3. **FindThatLead**: 50 búsquedas/mes gratis
4. **Voila Norbert**: 50 verificaciones gratis

**Truco:** Rotar entre todas = 300+ emails gratis/mes

---

### **🔐 MÉTODO 10: VERIFICACIÓN Y VALIDACIÓN**

```php
class EmailVerifier {
    
    public function verify($email) {
        list($user, $domain) = explode('@', $email);
        
        // 1. Verificar MX records
        if (!checkdnsrr($domain, 'MX')) {
            return false;
        }
        
        // 2. Verificar sintaxis
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            return false;
        }
        
        // 3. Verificar SMTP (sin enviar)
        $smtp = @fsockopen($domain, 25, $errno, $errstr, 5);
        if ($smtp) {
            fclose($smtp);
            return true;
        }
        
        return false;
    }
}
```

---

### **📊 TASAS DE ÉXITO POR MÉTODO**

```
Website scraping: 70% (si tienen web)
Pattern matching: 60% (empresas medianas/grandes)
Google dorks: 50% (información pública)
LinkedIn: 40% (perfiles completos)
Facebook: 35% (páginas activas)
WhatsApp: 30% (si usan Business)
Ingeniería social: 80% (pero manual)
```