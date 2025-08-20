from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from "./../services/pdf_importer.py" import process_test_pdfs 

class ProcessTestPDFsView(APIView):
    """
    View que recebe PDF da prova e PDF do gabarito,
    processa com o service e retorna lista de questões.
    """

    def post(self, request, *args, **kwargs):
        try:
            pdf_prova_file = request.FILES.get("pdf_prova")
            pdf_gabarito_file = request.FILES.get("pdf_gabarito")
            initial_params = request.data.get("initial_params")  # opcional (JSON)

            if not pdf_prova_file or not pdf_gabarito_file:
                return Response(
                    {"error": "É necessário enviar os arquivos 'pdf_prova' e 'pdf_gabarito'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Converte initial_params se vier em JSON
            if isinstance(initial_params, str):
                import json
                initial_params = json.loads(initial_params)

            processed_data = process_test_pdfs(pdf_prova_file, pdf_gabarito_file, initial_params)

            return Response(processed_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
