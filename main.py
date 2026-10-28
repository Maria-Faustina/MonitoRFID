import flet as ft


def main(page: ft.Page):
    page.title = "MonitorRFID"
    page.bgcolor = "#0E0E55"
    page.padding = 0
    page.spacing = 0
    page.window.width = 350
    page.window.height = 700
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def tela_home(e):
        page.views.clear()

        txt_painel = ft.Text(
            "Painel de Entrada",
            size=20,
            weight="bold",
            color="#0E0E55",
        )
        txt_registro = ft.Text(
            "Ultimos Acessos",
            size=15,
            weight="bold",
            color="#f0f0fc",
        )

        t_uid = ft.Text(
            "UID",
            expand=1,
            text_align=ft.TextAlign.CENTER,
            size=14,
            weight="bold",
            color="#f0f0fc",
        )
        t_status = ft.Text(
            "Status",
            expand=2,
            text_align=ft.TextAlign.CENTER,
            size=14,
            weight="bold",
            color="#f0f0fc",
        )
        t_dth = ft.Text(
            "Data Hora",
            expand=1,
            text_align=ft.TextAlign.CENTER,
            size=14,
            weight="bold",
            color="#f0f0fc",
        )

        title_painel = ft.Container(
            content=txt_painel,
            alignment=ft.Alignment.CENTER,
            padding=20,
        )

        linha_principal = ft.Container(
            content=ft.Row(
                controls=[t_uid, t_status, t_dth],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#0E0E55",
            border_radius=3,
            padding=3,
        )
        ft.Container(height=50)
        btn_liberar = ft.Container(
            content=ft.Button(
                content="Liberar acesso",
                icon=ft.Icons.LOCK_OPEN_SHARP,
                color="#5ed97c",
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
            ),
            padding=10,
            alignment=ft.Alignment.CENTER,
        )
        btn_voltar = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=tela_login,
                )
            ],
            alignment=ft.MainAxisAlignment.START,
        )
        lista_acessos = [
            ["A3 B2 C5 D1", "Liberado", "25/10/2026 16:15"],
            ["F8 4E 92 A0", "Negado", "25/10/2026 16:18"],
            ["12 C3 D4 E5", "Liberado", "25/10/2026 16:20"],
            ["7B 9A 2C 4D", "Negado", "25/10/2026 16:24"],
            ["7B 9A 2C 4D", "Negado", "25/10/2026 16:24"],
        ]

        lista_dados = ft.ListView(padding=0, spacing=0)
        for uid, status, dth in lista_acessos:
            if status == "Liberado":
                cor_status = "#5ed97c"
            else:
                cor_status = "#ff6b6b"

            lista_dados.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                uid,
                                color="#f0f0fc",
                                expand=1,
                                size=12,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                status,
                                color=cor_status,
                                expand=2,
                                size=13,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                dth,
                                color="#f0f0fc",
                                expand=1,
                                size=13,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor="#0E0E55",
                    border_radius=3,
                    padding=3,
                    margin=3,
                )
            )
        painel_fundo = ft.Container(
            content=ft.Column(
                controls=[txt_registro, linha_principal, lista_dados],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.Alignment.TOP_CENTER,
            bgcolor="#021433",
            margin=1,
            padding=5,
            border_radius=5,
            width=330,
            height=330,
        )

        page.views.append(
            ft.View(
                route="/tela_home",
                controls=[
                    title_painel,
                    painel_fundo,
                    btn_liberar,
                    btn_voltar,
                ],
                bgcolor="#ABDCDC",
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                vertical_alignment=ft.MainAxisAlignment.CENTER,
            )
        )
        page.update()

    def tela_login(e=None):
        page.views.clear()

        painel_login = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Login",
                        size=30,
                        weight="bold",
                        color="#f0f0fc",
                    ),
                    ft.Container(height=10),
                    ft.TextField(
                        label="Insira seu nome de usuario",
                        label_style=ft.TextStyle(size=10),
                        bgcolor="#f0f0fc",
                        width=200,
                        height=38,
                    ),
                    ft.TextField(
                        label="Insira sua senha",
                        password=True,
                        can_reveal_password=True,
                        bgcolor="#f0f0fc",
                        label_style=ft.TextStyle(size=10),
                        width=200,
                        height=38,
                    ),
                    ft.Container(height=10),
                    ft.Button(
                        content="Fazer login",
                        on_click=tela_home,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            width=300,
            height=330,
            padding=30,
            border_radius=12,
            bgcolor="#0F3372",
            alignment=ft.Alignment.CENTER,
        )

        page.views.append(
            ft.View(
                route="/tela_login",
                controls=[painel_login],
                bgcolor="#ABDCDC",
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        page.update()

    def troca_tela():
        if page.route == "/tela_login":
            tela_login()
        elif page.route == "/tela_home":
            tela_home(None)

    page.on_route_change = lambda _: troca_tela()
    page.navigate("/tela_login")


ft.run(main)
