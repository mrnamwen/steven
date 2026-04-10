#include "StevenApp.h"
#include <NiMain.h>

//---------------------------------------------------------------------------
NiApplication* NiApplication::Create()
{
    return NiNew StevenApp;
}
//---------------------------------------------------------------------------
StevenApp::StevenApp()
    : NiApplication("Steven - SMT:Imagine Client", 1280, 720, false)
    , m_fCamDistance(50.0f)
    , m_fCamYaw(0.0f)
    , m_fCamPitch(0.3f)
    , m_kCamTarget(0.0f, 0.0f, 0.0f)
{
}
//---------------------------------------------------------------------------
bool StevenApp::Initialize()
{
    if (!NiApplication::Initialize())
        return false;

    return true;
}
//---------------------------------------------------------------------------
bool StevenApp::CreateScene()
{
    m_spScene = NiNew NiNode;

    // Create a simple colored triangle to prove the renderer works.
    // Three vertices, one triangle face.
    unsigned short usVertices = 3;
    unsigned short usTriangles = 1;

    NiTriShape* pkTriShape = NiNew NiTriShape(usVertices, NiPoint3::ZERO,
        NULL, NULL, NULL, usTriangles);

    // Vertex positions (a triangle in the XZ plane, Y-up)
    NiPoint3* pkVertex = pkTriShape->GetVertices();
    pkVertex[0] = NiPoint3(-10.0f, 0.0f, -10.0f);
    pkVertex[1] = NiPoint3( 10.0f, 0.0f, -10.0f);
    pkVertex[2] = NiPoint3(  0.0f, 0.0f,  10.0f);

    // Normals (all pointing up)
    NiPoint3* pkNormal = NiNew NiPoint3[usVertices];
    pkNormal[0] = NiPoint3(0.0f, 1.0f, 0.0f);
    pkNormal[1] = NiPoint3(0.0f, 1.0f, 0.0f);
    pkNormal[2] = NiPoint3(0.0f, 1.0f, 0.0f);
    pkTriShape->SetNormals(pkNormal);

    // Vertex colors (red, green, blue)
    NiColorA* pkColors = NiNew NiColorA[usVertices];
    pkColors[0] = NiColorA(1.0f, 0.0f, 0.0f, 1.0f);
    pkColors[1] = NiColorA(0.0f, 1.0f, 0.0f, 1.0f);
    pkColors[2] = NiColorA(0.0f, 0.0f, 1.0f, 1.0f);
    pkTriShape->SetColors(pkColors);

    // Triangle index
    unsigned short* pusTriList = pkTriShape->GetTriList();
    pusTriList[0] = 0;
    pusTriList[1] = 1;
    pusTriList[2] = 2;

    // Vertex color property so the colors are visible
    NiVertexColorProperty* pkVCProp = NiNew NiVertexColorProperty;
    pkVCProp->SetSourceMode(NiVertexColorProperty::SOURCE_EMISSIVE);
    pkVCProp->SetLightingMode(NiVertexColorProperty::LIGHTING_E);
    pkTriShape->AttachProperty(pkVCProp);

    // Update model bound
    pkTriShape->SetModelBound(NiBound(NiPoint3::ZERO, 15.0f));

    m_spTriNode = NiNew NiNode;
    m_spTriNode->AttachChild(pkTriShape);

    m_spScene->AttachChild(m_spTriNode);
    m_spScene->Update(0.0f);

    return true;
}
//---------------------------------------------------------------------------
bool StevenApp::CreateCamera()
{
    m_spCamera = NiNew NiCamera;

    // Perspective frustum
    NiFrustum kFrustum;
    kFrustum.m_fLeft   = -0.5f;
    kFrustum.m_fRight  =  0.5f;
    kFrustum.m_fTop    =  0.5f;
    kFrustum.m_fBottom = -0.5f;
    kFrustum.m_fNear   =  1.0f;
    kFrustum.m_fFar    = 10000.0f;
    m_spCamera->SetViewFrustum(kFrustum);

    // Adjust for window aspect ratio
    float fAspect = (float)m_pkAppWindow->GetWidth() /
                    (float)m_pkAppWindow->GetHeight();
    m_spCamera->AdjustAspectRatio(fAspect);

    // Position: orbit around origin
    float fX = m_fCamDistance * NiCos(m_fCamPitch) * NiSin(m_fCamYaw);
    float fY = m_fCamDistance * NiSin(m_fCamPitch);
    float fZ = m_fCamDistance * NiCos(m_fCamPitch) * NiCos(m_fCamYaw);

    m_spCamera->SetTranslate(m_kCamTarget + NiPoint3(fX, fY, fZ));
    m_spCamera->LookAtWorldPoint(m_kCamTarget, NiPoint3(0.0f, 1.0f, 0.0f));
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

    float fDeltaTime = GetFrameTime();
    float fRotSpeed = 2.0f;
    float fZoomSpeed = 50.0f;

    // Arrow keys rotate the camera orbit
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_LEFT))
        m_fCamYaw -= fRotSpeed * fDeltaTime;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_RIGHT))
        m_fCamYaw += fRotSpeed * fDeltaTime;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_UP))
        m_fCamPitch += fRotSpeed * fDeltaTime;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_DOWN))
        m_fCamPitch -= fRotSpeed * fDeltaTime;

    // +/- zoom
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_ADD))
        m_fCamDistance -= fZoomSpeed * fDeltaTime;
    if (pkKeyboard->KeyIsDown(NiInputKeyboard::KEY_SUBTRACT))
        m_fCamDistance += fZoomSpeed * fDeltaTime;

    // Clamp pitch
    if (m_fCamPitch > 1.4f) m_fCamPitch = 1.4f;
    if (m_fCamPitch < -1.4f) m_fCamPitch = -1.4f;
    if (m_fCamDistance < 5.0f) m_fCamDistance = 5.0f;
}
//---------------------------------------------------------------------------
void StevenApp::UpdateFrame()
{
    // Update camera position from orbit parameters
    float fX = m_fCamDistance * NiCos(m_fCamPitch) * NiSin(m_fCamYaw);
    float fY = m_fCamDistance * NiSin(m_fCamPitch);
    float fZ = m_fCamDistance * NiCos(m_fCamPitch) * NiCos(m_fCamYaw);

    m_spCamera->SetTranslate(m_kCamTarget + NiPoint3(fX, fY, fZ));
    m_spCamera->LookAtWorldPoint(m_kCamTarget, NiPoint3(0.0f, 1.0f, 0.0f));
    m_spCamera->Update(m_fAccumTime);

    NiApplication::UpdateFrame();
}
//---------------------------------------------------------------------------
