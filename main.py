import asyncio
import socket

import flet as ft
import requests
import socketio

SERVER_URL = ""  # preenchido pela descoberta (ou manualmente, como fallback)
DISCOVERY_PORT = 5001
DISCOVERY_REQUEST = b"MONITORRFID_DISCOVER"


def descobrir_servidor():
    """Procura o app.py por UDP broadcast na rede local."""
    global SERVER_URL
    if SERVER_URL:
        return SERVER_URL

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(1.5)
        try:
            sock.sendto(DISCOVERY_REQUEST, ("255.255.255.255", DISCOVERY_PORT))
            dados, _ = sock.recvfrom(1024)
            _, ip, porta = dados.decode().strip().split("|")  # MONITORRFID_SERVER|ip|porta
            SERVER_URL = f"http://{ip}:{porta}"
        except (OSError, ValueError):
            pass
    return SERVER_URL


def main(page: ft.Page):
    page.title = "MonitorRFID"
    page.bgcolor = "#0E0E55"
    page.padding = 0
    page.window.width = 350
    page.window.height = 700

    sio = socketio.Client(reconnection=True)

    # estado compartilhado entre as telas e os eventos do socket
    estado = {"token": None, "historico": [], "lista": None, "txt_conexao": None}

    # ---------- componentes reutilizáveis ----------
    def mostrar_aviso(texto, cor):
        page.show_dialog(ft.SnackBar(content=ft.Text(texto, color="#dedee7"), bgcolor=cor, duration=1500))
        page.update()

    def linha(a, b, c, cor_b="#dedee7", cabecalho=False):
        """Linha de 3 colunas (UID | Status | Data Hora), usada no cabeçalho e nos registros."""
        kw = dict(size=14, weight="bold") if cabecalho else dict(size=12)
        celulas = [
            ft.Text(t, color=cor, expand=e, text_align=ft.TextAlign.CENTER, **kw)
            for t, cor, e in ((a, "#dedee7", 1), (b, cor_b, 2), (c, "#dedee7", 1))
        ]
        return ft.Container(
            content=ft.Row(
                celulas,
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#263A6D",
            border_radius=3,
            padding=3,
            margin=0 if cabecalho else 3,
        )

    def linhas_historico():
        controles = []
        for r in estado["historico"]:
            liberado = str(r["status"]).lower() == "liberado"
            uid = "Painel Admin" if "MANUAL" in str(r["uid"]) else r["uid"]
            controles.append(linha(uid, "Liberado" if liberado else "Negado", r["data_hora"],
                                   "#5ed97c" if liberado else "#ff6b6b"))
        return controles

    def campo(dica, **kw):
        return ft.TextField(
            hint_text=dica,
            hint_style=ft.TextStyle(size=10),
            color="#090909",
            bgcolor="#f0f0fc",
            width=225,
            height=38,
            cursor_height=20,
            border=ft.OutlineInputBorder(
                border_radius=ft.BorderRadius.all(20),
                side=ft.BorderSide(color="#f0f0fc"),
            ),
            **kw,
        )

    def nova_tela(rota, *controles):
        page.views.append(
            ft.View(
                route=rota,
                controls=list(controles),
                bgcolor="#ABDCDC",
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                vertical_alignment=ft.MainAxisAlignment.CENTER,
            )
        )

    # ---------- Socket.IO ----------
    def renderizar_lista():
        if estado["lista"] is not None:
            estado["lista"].controls = linhas_historico()
            page.update()

    def atualizar_conexao(conectado):
        txt = estado["txt_conexao"]
        if txt is not None:
            txt.value = "Servidor: conectado" if conectado else "Servidor: desconectado"
            txt.color = "#2e7d32" if conectado else "#c62828"
            page.update()

    def ao_receber_historico(lista):
        estado["historico"] = list(lista)[:5]
        renderizar_lista()

    def ao_novo_acesso(registro):
        estado["historico"] = ([registro] + estado["historico"])[:5]
        renderizar_lista()

    sio.on("connect", lambda: atualizar_conexao(True))
    sio.on("disconnect", lambda *_: atualizar_conexao(False))
    sio.on("historico", ao_receber_historico)
    sio.on("novo_acesso", ao_novo_acesso)
    sio.on("erro", lambda msg: mostrar_aviso(str(msg), "red"))

    def conectar_servidor():
        if sio.connected:
            return

        def _conectar():
            try:
                # se a descoberta falhar, a URL vazia gera erro e cai no except
                sio.connect(descobrir_servidor(), auth={"token": estado["token"]}, wait_timeout=5)
            except Exception:
                atualizar_conexao(False)

        page.run_thread(_conectar)

    def liberar_acesso():
        if not sio.connected:
            mostrar_aviso("Sem conexão com o servidor. Tentando reconectar...", "red")
            conectar_servidor()
            return
        sio.emit("liberar_acesso")  # o servidor registra e devolve "novo_acesso"

    def sair():
        if sio.connected:
            sio.disconnect()
        estado["token"] = None
        page.run_task(page.push_route, "/tela_login")

    # ---------- telas ----------
    def tela_home():
        estado["txt_conexao"] = ft.Text("Servidor: desconectado", size=12, color="#c62828")
        estado["lista"] = ft.ListView(controls=linhas_historico(), padding=0)

        nova_tela(
            "/tela_home",
            ft.Container(
                ft.Column(
                    [ft.Text("Painel de Entrada", size=20, weight="bold", color="#0E0E55"), estado["txt_conexao"]],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                ),
                alignment=ft.Alignment.CENTER,
                padding=40,
            ),
            ft.Container(
                ft.Column(
                    [
                        ft.Container(
                            ft.Text("Ultimos Acessos", size=15, weight="bold", color="#dedee7"),
                            alignment=ft.Alignment.CENTER,
                        ),
                        linha("UID", "Status", "Data Hora", cabecalho=True),
                        estado["lista"],
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.Alignment.TOP_CENTER,
                blur=ft.Blur(sigma_x=10, sigma_y=10, tile_mode=ft.BlurTileMode.MIRROR),
                bgcolor="#0E3155",
                margin=1,
                padding=5,
                border_radius=5,
                width=320,
                height=330,
            ),
            ft.Container(
                ft.Button(
                    on_click=liberar_acesso,
                    content="Liberar acesso",
                    icon=ft.Icons.LOCK_OPEN_SHARP,
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(width=1, color="#CCCFD8"),
                        shape=ft.RoundedRectangleBorder(radius=5),
                    ),
                    width=310,
                    height=50,
                    bgcolor="#e5e5f0",
                    color="#529d65",
                ),
                alignment=ft.Alignment.CENTER,
            ),
            ft.Row([ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color="#263A6D", on_click=sair)]),
        )

        if sio.connected:
            atualizar_conexao(True)
        else:
            conectar_servidor()

    def tela_login():
        async def entrar():
            if not (campo_email.value and campo_senha.value):
                mostrar_aviso("Preencha todos os campos!", "red")
                return

            servidor = await asyncio.to_thread(descobrir_servidor)
            if not servidor:
                mostrar_aviso("Servidor não encontrado na rede Wi-Fi", "red")
                return
            try:
                resp = await asyncio.to_thread(
                    requests.post,
                    f"{servidor}/api/login",
                    json={"usuario": campo_email.value, "senha": campo_senha.value},
                    timeout=5,
                )
            except requests.RequestException:
                mostrar_aviso("Não foi possível conectar ao servidor", "red")
                return

            if resp.status_code == 200:
                estado["token"] = resp.json().get("token")
                mostrar_aviso("Login realizado com sucesso!", "green")
                await asyncio.sleep(1)
                page.run_task(page.push_route, "/tela_home")
            else:
                mostrar_aviso("Usuário ou senha incorretos!", "red")

        campo_email = campo("Insira seu nome de usuario")
        campo_senha = campo("Insira sua senha", password=True, can_reveal_password=True)

        nova_tela(
            "/tela_login",
            ft.Container(
                ft.Column(
                    [
                        ft.Text("MonitorRFID", size=30, weight="bold", color="#020230"),
                        ft.Container(height=15),
                        ft.Image(src="icons/logo_trans.png", width=65, height=65),
                        ft.Container(height=20),
                        campo_email,
                        campo_senha,
                        ft.Container(height=10),
                        ft.Button(content="Fazer Login", on_click=entrar,
                                  bgcolor="#f0f0fc", color="#030345", width=150, height=35),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                width=300,
                height=400,
                padding=30,
                border_radius=12,
                blur=ft.Blur(sigma_x=10, sigma_y=10, tile_mode=ft.BlurTileMode.MIRROR),
                bgcolor="#43F0FDFF",
                alignment=ft.Alignment.CENTER,
            ),
        )

    telas = {"/tela_login": tela_login, "/tela_home": tela_home}

    def troca_tela():
        page.views.clear()
        if page.route in telas:
            telas[page.route]()
        page.update()

    page.on_route_change = troca_tela
    page.run_task(page.push_route, "/tela_login")


ft.run(main)
