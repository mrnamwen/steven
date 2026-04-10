#include "StevenApp.h"
#include <NiMain.h>
#include <NiStream.h>

//---------------------------------------------------------------------------
NiApplication* NiApplication::Create()
{
    return NiNew StevenApp;
}
//---------------------------------------------------------------------------
StevenApp::StevenApp()
    : NiApplication("Steven - SMT:Imagine Client", 1280, 720, false)
    , m_kCamPos(0.0f, 50.0f, 0.0f)
    , m_fCamYaw(0.0f)
    , m_fCamPitch(0.0f)
    , m_fMoveSpeed(100.0f)
    , m_fLookSpeed(2.0f)
{
    SetMediaPath("./assets/zones/");
}
//---------------------------------------------------------------------------
bool StevenApp::Initialize()
{
    if (!NiApplication::Initialize())
        return false;

    return true;
}
//---------------------------------------------------------------------------
bool StevenApp::LoadZoneNIF(const char* pcFilename)
{
    NiStream kStream;

    NiOutputDebugString("Loading zone: ");
    NiOutputDebugString(pcFilename);
    NiOutputDebugString("\n");

    bool bSuccess = kStream.Load(
        NiApplication::ConvertMediaFilename(pcFilename));

    if (!bSuccess)
    {
        NiOutputDebugString("Failed to load zone NIF!\n");
        return false;
    }

    // First object should be the scene graph root
    unsigned int uiObjects = kStream.GetObjectCount();
    NiOutputDebugString("NIF objects: ");

    for (unsigned int i = 0; i < uiObjects; i++)
    {
        NiObject* pkObj = kStream.GetObjectAt(i);
        if (pkObj && NiIsKindOf(NiNode, pkObj))
        {
            NiNode* pkNode = (NiNode*)pkObj;
            m_spScene->AttachChild(pkNode);
            NiOutputDebugString("  Attached scene node\n");
        }
    }

    // Update transforms
    m_spScene->Update(0.0f);
    m_spScene->UpdateProperties();

    return true;
}
//---------------------------------------------------------------------------
bool StevenApp::CreateScene()
{
    // Alpha accumulator for proper transparency sorting
    NiAlphaAccumulator* pkAccum = NiNew NiAlphaAccumulator;
    m_spRenderer->SetSorter(pkAccum);

    m_spScene = NiNew NiNode;

    // Try to load zone NIFs - try several in order
    const char* zones[] = {
        "ClientDebugMap.nif",
        "MA01_001_01.nif",
        "MB01_001_01.nif",
        NULL
    };

    bool bLoaded = false;
    for (int i = 0; zones[i] != NULL; i++)
    {
        if (LoadZoneNIF(zones[i]))
        {
            bLoaded = true;
            break;
        }
    }

    if (!bLoaded)
    {
        NiOutputDebugString("No zone NIF found. Running with empty scene.\n");
    }

    m_spScene->UpdateEffects();
    m_spScene->Update(0.0f);

    return true;
}
//---------------------------------------------------------------------------
bool StevenApp::CreateCamera()
{
    m_spCamera = NiNew NiCamera;

    NiFrustum kFrustum;
    kFrustum.m_fLeft   = -0.5f;
    kFrustum.m_fRight  =  0.5f;
    kFrustum.m_fTop    =  0.5f;
    kFrustum.m_fBottom = -0.5f;
    kFrustum.m_fNear   =  1.0f;
    kFrustum.m_fFar    = 50000.0f;
    m_spCamera->SetViewFrustum(kFrustum);

    float fAspect = (float)m_pkAppWindow->GetWidth() /
                    (float)m_pkAppWindow->GetHeight();
    m_spCamera->AdjustAspectRatio(fAspect);

    m_spCamera->SetTranslate(m_kCamPos);
    m_spCamera->Update(0.0f);

    return true;
}
//---------------------------------------------------------------------------
void StevenApp::ProcessInput()
{
    NiApplication::ProcessInput();

    NiInputKeyboard* pkKeyboard = GetInputSystem()->GetKeyboard();
    if (!pkKeyboard)
        return;

    float dt = GetFrameTime();
    if (dt <= 0.0f || dt > 0.5f)
        dt = 0.016f;

    // Mouse look (right mouse button or always)
    NiInputMouse* pkMouse = GetInputSystem()->GetMouse();
    if (pkMouse)
    {
        int iDX = 0, iDY = 0;
        pkMouse->GetPositionDelta(iDX, iDY);

        if (pkMouse->ButtonIsDown(NiInputMouse::NIM_RIGHT))
        {
            m_fCamYaw   -= (float)iDX * m_fLookSpeed * 0.003f;
            m_fCamPitch -= (float)iDY * m_fLookSpeed * 0.003f;
        }
    }

    // Arrow keys also rotate
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_LEFT))
        m_fCamYaw += m_fLookSpeed * dt;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_RIGHT))
        m_fCamYaw -= m_fLookSpeed * dt;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_UP))
        m_fCamPitch += m_fLookSpeed * dt;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_DOWN))
        m_fCamPitch -= m_fLookSpeed * dt;

    // Clamp pitch
    if (m_fCamPitch >  1.4f) m_fCamPitch =  1.4f;
    if (m_fCamPitch < -1.4f) m_fCamPitch = -1.4f;

    // Calculate forward/right vectors from yaw/pitch
    float fCosP = NiCos(m_fCamPitch);
    NiPoint3 kForward(
        fCosP * NiSin(m_fCamYaw),
        NiSin(m_fCamPitch),
        fCosP * NiCos(m_fCamYaw)
    );
    NiPoint3 kRight(
        NiCos(m_fCamYaw),
        0.0f,
        -NiSin(m_fCamYaw)
    );
    NiPoint3 kUp(0.0f, 1.0f, 0.0f);

    float fSpeed = m_fMoveSpeed;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_LSHIFT))
        fSpeed *= 5.0f;

    // WASD movement
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_W))
        m_kCamPos += kForward * fSpeed * dt;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_S))
        m_kCamPos -= kForward * fSpeed * dt;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_A))
        m_kCamPos -= kRight * fSpeed * dt;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_D))
        m_kCamPos += kRight * fSpeed * dt;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_SPACE))
        m_kCamPos += kUp * fSpeed * dt;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_LCONTROL))
        m_kCamPos -= kUp * fSpeed * dt;
}
//---------------------------------------------------------------------------
void StevenApp::UpdateFrame()
{
    // Update camera transform from fly-camera state
    float fCosP = NiCos(m_fCamPitch);
    NiPoint3 kForward(
        fCosP * NiSin(m_fCamYaw),
        NiSin(m_fCamPitch),
        fCosP * NiCos(m_fCamYaw)
    );

    m_spCamera->SetTranslate(m_kCamPos);
    m_spCamera->LookAtWorldPoint(
        m_kCamPos + kForward,
        NiPoint3(0.0f, 1.0f, 0.0f));
    m_spCamera->Update(m_fAccumTime);

    NiApplication::UpdateFrame();
}
//---------------------------------------------------------------------------
