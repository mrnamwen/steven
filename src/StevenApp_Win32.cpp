#include "StevenApp.h"
#include <NiDX9Renderer.h>

//---------------------------------------------------------------------------
bool StevenApp::CreateRenderer()
{
    unsigned int uiWidth = m_pkAppWindow->GetWidth();
    unsigned int uiHeight = m_pkAppWindow->GetHeight();

    m_spRenderer = NiDX9Renderer::Create(uiWidth, uiHeight,
        NiDX9Renderer::USE_NOFLAGS, GetWindowReference(),
        GetRenderWindowReference());

    if (m_spRenderer == NULL)
    {
        NiMessageBox("Failed to create D3D9 renderer.", "Steven Error");
        QuitApplication();
        return false;
    }

    m_spRenderer->SetBackgroundColor(NiColor(0.05f, 0.05f, 0.1f));

    return true;
}
//---------------------------------------------------------------------------
