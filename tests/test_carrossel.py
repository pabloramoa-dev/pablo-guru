import unittest
from datetime import date, timedelta
from carrossel.banco import BANCO, INICIO
from carrossel.gerar import do_dia, legenda, normalizar, problemas


class CarrosselTests(unittest.TestCase):
    def test_banco_passa_na_revisao(self):
        for item in BANCO:
            with self.subTest(item=item['id']):
                self.assertEqual(problemas(normalizar(item)), [])

    def test_um_por_dia_sem_repetir(self):
        vistos = set()
        for i in range(len(BANCO)):
            dia = (date.fromisoformat(INICIO) + timedelta(days=i)).isoformat()
            c = do_dia(dia)
            self.assertNotIn(c['id'], vistos)
            vistos.add(c['id'])

    def test_legenda(self):
        txt = legenda(normalizar(BANCO[0]))
        self.assertIn('@opabloguru', txt)
        self.assertLessEqual(txt.count('#'), 10)
        self.assertLessEqual(len(txt), 2200)

    def test_promessa_de_cura_reprovada(self):
        c = normalizar(BANCO[0])
        c['slides'][0]['texto'] = 'Esta prática cura a ansiedade, garantido.'
        self.assertTrue(any('proibido' in p for p in problemas(c)))


if __name__ == '__main__':
    unittest.main()
