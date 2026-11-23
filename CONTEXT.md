# Laboratório de dados do Datamart

Vocabulário do ambiente usado para desenvolver, consultar e visualizar
dados orçamentários da SPLOR.

## Language

**Administrador do laboratório**:
Destinatário que administra integralmente as ferramentas do laboratório
e a máquina que as hospeda, com autonomia para conduzir seu trabalho.
_Avoid_: usuário limitado, usuário do painel, usuário sem qualificar sua autoridade

**Operador da plataforma**:
Pessoa responsável pelo painel de hospedagem e pela plataforma em que
o laboratório é disponibilizado.
_Avoid_: administrador, quando não se distingue a plataforma do laboratório

**Agente do laboratório**:
Automação de IA que trabalha nas ferramentas do laboratório por delegação
do administrador, que escolhe como conduzir essa delegação.
_Avoid_: operador da plataforma, quando se trata de uma automação do administrador

**Entrega operacional**:
Disponibilização das ferramentas e do acesso administrativo para que
o destinatário possa trabalhar no laboratório.
_Avoid_: carga inicial de dados, implantação do pipeline analítico

**Base analítica**:
Conjunto de dados orçamentários utilizado no desenvolvimento e nas
consultas do laboratório.
_Avoid_: banco, sem especificar a finalidade

**Base de configuração do Metabase**:
Conjunto de informações que mantém usuários, permissões, perguntas e
painéis da ferramenta.
_Avoid_: base analítica, banco do Metabase quando se refere à fonte de dados
